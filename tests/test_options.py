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
