import logging
import os
import tempfile

import pandas as pd

from pandas_checks import options


def test_set_format():
    options.set_format(precision=3, use_emojis=False)
    assert pd.get_option("pdchecks.precision") == 3
    assert pd.get_option("pdchecks.use_emojis") == False
    options.reset_format()


def test_reset_format():
    options.set_format(precision=5, use_emojis=True)
    options.reset_format()
    assert pd.get_option("pdchecks.precision") == 2
    assert pd.get_option("pdchecks.use_emojis") == True


def test_set_mode():
    options.set_mode(enable_checks=False, enable_asserts=False)
    assert pd.get_option("pdchecks.enable_checks") == False
    assert pd.get_option("pdchecks.enable_asserts") == False
    options.set_mode(enable_checks=True, enable_asserts=True)  # reset


def test_get_mode():
    options.set_mode(enable_checks=True, enable_asserts=True)
    mode = options.get_mode()
    assert mode["enable_checks"] == True
    assert mode["enable_asserts"] == True


def test_enable_checks():
    options.disable_checks()
    options.enable_checks()
    assert pd.get_option("pdchecks.enable_checks") == True
    assert pd.get_option("pdchecks.enable_asserts") == True


def test_disable_checks():
    options.enable_checks()
    options.disable_checks(enable_asserts=False)
    assert pd.get_option("pdchecks.enable_checks") == False
    assert pd.get_option("pdchecks.enable_asserts") == False
    options.enable_checks()  # Reset


def test_register_option_valid():
    options._register_option("test_option", 10, "", lambda x: isinstance(x, int))
    assert pd.get_option("pdchecks.test_option") == 10


def test_register_option_existing():
    options._set_option("precision", 17)
    options._register_option("precision", 10, "", lambda x: isinstance(x, int))
    assert pd.get_option("pdchecks.precision") == 10


def test_set_custom_print_fn(iris):
    """Test setting a custom print function that logs outputs to a file."""

    # Create a temporary log file
    with tempfile.NamedTemporaryFile(delete=False, mode="w+") as tmpfile:
        log_path = tmpfile.name

    # Set up logging to file using an explicit FileHandler
    # To avoid issues with the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(log_path, mode="w")
    formatter = logging.Formatter("%(levelname)s:%(name)s:%(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    try:
        # Set custom print function to logging.info
        options.set_custom_print_fn(custom_print_fn=logging.info, print_to_stdout=False)

        # Run checks
        iris.check.columns()
        iris.check.describe()
        iris.check.assert_float(raise_exception=False)

        # Reset custom print function
        options.set_custom_print_fn(custom_print_fn=None, print_to_stdout=True)

        # Ensure all logs are flushed
        file_handler.flush()
        logger.handlers[0].flush()

        # Read log file
        with open(log_path, "r") as f:
            log_content = f.read()
    finally:
        # Clean up temp file and remove handler
        logger.removeHandler(file_handler)
        file_handler.close()
        os.remove(log_path)

    # Assert expected log output is present
    assert (
        log_content.strip()
        == """INFO:root:🏛️ Columns: ['sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'species']
INFO:root:📏 Distributions
INFO:root:           sepal_length  sepal_width  petal_length  petal_width
    count    150.000000   150.000000    150.000000   150.000000
    mean       5.843333     3.057333      3.758000     1.199333
    std        0.828066     0.435866      1.765298     0.762238
    min        4.300000     2.000000      1.000000     0.100000
    25%        5.100000     2.800000      1.600000     0.300000
    50%        5.800000     3.000000      4.350000     1.300000
    75%        6.400000     3.300000      5.100000     1.800000
    max        7.900000     4.400000      6.900000     2.500000
INFO:root: ㄨ Assert type failed: expected  float, got float64, float64, float64, float64, object

""".strip()
    )  # fmt: skip
