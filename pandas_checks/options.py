"""Utilities for configuring Pandas Checks options.

This module provides functions for setting and managing global options for
Pandas Checks, including formatting and disabling checks and assertions.
"""

from typing import Any, Callable, Dict, List, Union

import pandas as pd
import pandas._config.config as cf


# -----------------------
# Helpers
# -----------------------
def _set_option(option: str, value: Any) -> None:
    """Updates the value of a Pandas Checks option in the global Pandas context manager.

    Args:
        option: The name of the option to set.
        value: The value to set for the option.

    Returns:
        None

    Raises:
        AttributeError: If the `option` is not a valid Pandas Checks option.
    """
    pdchecks_option = (
        option if option.startswith("pdchecks.") else "pdchecks." + option
    )  # Fully qualified
    if pdchecks_option in pd._config.config._select_options("pdchecks"):
        pd.set_option(pdchecks_option, value)
    else:
        raise AttributeError(
            f"No Pandas Checks option for {pdchecks_option}. Available options: {pd._config.config._select_options('pdchecks')}"
        )


def _register_option(
    name: str, default_value: Any, description: str, validator: Callable
) -> None:
    """Registers a Pandas Checks option in the global Pandas context manager.

    If the option has already been registered, reset its value.

    This method enables setting global formatting for Pandas Checks results and storing
    variables that will persist across Pandas method chains, which return newly
    initialized DataFrames at each method (and so reset the DataFrame's attributes).

    Args:
        name: The name of the option to register.
        default_value: The default value for the option.
        description: A description of the option.
        validator: A function to validate the option value.

    Returns:
        None

    Note:
        For more details on the arguments, see the documentation for
        pandas._config.config.register_option()
    """
    key_name = (
        name if "pdchecks." not in name else name.replace("pdchecks.", "")
    )  # If we passed pdchecks.name, strip pdchecks., since we'll be working in "checks" config namespace

    # Option already registered?
    try:
        pd.get_option(f"pdchecks.{key_name}")
        pd.set_option(f"pdchecks.{key_name}", default_value)  # Reset its value
    # Option not registered yet?
    except pd.errors.OptionError:
        with cf.config_prefix("pdchecks"):
            # Register it!
            cf.register_option(key_name, default_value, description, validator)


# -----------------------
# Formatting
# -----------------------


def set_format(**kwargs: Any) -> None:
    """Configures selected formatting options for Pandas Checks. Run pandas_checks.describe_options() to see a list of available options.

    For example, set_format(check_text_tag= "h1", use_emojis=False`)
    will globally change Pandas Checks to display text results as H1 headings and remove all emojis.

    Returns:
        None

    Args:
        **kwargs: Pairs of setting name and its new value.

    """
    for arg, value in kwargs.items():
        _set_option(arg, value)


def reset_format() -> None:
    """Globally restores all Pandas Checks formatting options to their default "factory" settings.

    Returns:
        None
    """
    _initialize_format_options()


def _initialize_format_options(options: Union[List[str], None] = None) -> None:
    """Initializes or resets Pandas Checks formatting options.

    Args:
        options (Union[List[str], None], optional): A list of option names to initialize or reset.
            If None, all formatting options will be initialized or reset.
    Returns:
        None

    Note:
        We separate this function from _initialize_options() so user can reset just formatting without changing mode

    """
    option_keys = (
        [option.replace("pdchecks.", "") for option in options] if options else []
    )
    if "precision" in option_keys or options == None:
        _register_option(
            name="precision",
            default_value=2,
            description="""
    : float
    The floating point output precision of Pandas Checks outputs in IPython/Jupyter, in terms of number of places after the decimal, for regular formatting as well as scientific notation. Similar to ``precision`` in :meth:`numpy.set_printoptions`. Does not change precision in Pandas Checks output in terminal. Does not change precision of other Pandas operations, only Pandas Checks: to change Pandas precision, use pd.set_option('display.precision',...).
    """,
            validator=cf.is_nonnegative_int,
        )
    if "table_row_hover_style" in option_keys or options == None:
        _register_option(
            name="table_row_hover_style",
            default_value={
                "selector": "tr:hover",
                "props": [("background-color", "#2986cc")],
            },
            description="""
    : dict
    The background color to show when hovering over a Pandas Checks table`.
    """,
            validator=cf.is_instance_factory(dict),
        )
    if "use_emojis" in option_keys or options == None:
        _register_option(
            name="use_emojis",
            default_value=True,
            description="""
    : bool
    Whether Pandas Checks `check_names` text should keep emojis. This includes default check_names from the factory and user-supplied check_names`.
    """,
            validator=cf.is_instance_factory(bool),
        )
    if "indent_table_terminal" in option_keys or options == None:
        _register_option(
            name="indent_table_terminal",
            default_value=4,
            description="""
    : int
    Number of spaces to indent Pandas Checks tables in terminal display.
    """,
            validator=cf.is_instance_factory(int),
        )
    if "indent_table_plot_ipython" in option_keys or options == None:
        _register_option(
            name="indent_table_plot_ipython",
            default_value=30,
            description="""
    : int
    Number of pixels to indent Pandas Checks tables or plots in IPython/Jupyter display.
    """,
            validator=cf.is_instance_factory(int),
        )
    # Text styling
    if "check_text_tag" in option_keys or options == None:
        _register_option(
            name="check_text_tag",
            default_value="h5",
            description="""
    : str
    A single HTML tag (h1, h5, p, etc) that Pandas Checks will use when displaying results that are lines of text.
    """,
            validator=cf.is_instance_factory(str),
        )

    if "table_title_tag" in option_keys or options == None:
        _register_option(
            name="table_title_tag",
            default_value="h5",
            description="""
    : str
    A single HTML tag (h1, h5, p, etc) that Pandas Checks will use for the titles of tables.
    """,
            validator=cf.is_instance_factory(str),
        )

    if "plot_title_tag" in option_keys or options == None:
        _register_option(
            name="plot_title_tag",
            default_value="h5",
            description="""
    : str
    A single HTML tag (h1, h5, p, etc) that Pandas Checks will use for the titles of plots and histograms.
    """,
            validator=cf.is_instance_factory(str),
        )

    if "fail_message_fg_color" in option_keys or options == None:
        _register_option(
            name="fail_message_fg_color",
            default_value="white",
            description="""
    : str
    The foreground color that Pandas Checks will use for the lead-in text when assert_data() fails.
    """,
            validator=cf.is_instance_factory(str),
        )

    if "fail_message_bg_color" in option_keys or options == None:
        _register_option(
            name="fail_message_bg_color",
            default_value="red",
            description="""
    : str
    The background color that Pandas Checks will use for the lead-in text when assert_data() fails.
    """,
            validator=cf.is_instance_factory(str),
        )

    if "pass_message_fg_color" in option_keys or options == None:
        _register_option(
            name="pass_message_fg_color",
            default_value="black",
            description="""
    : str
    The foreground color that Pandas Checks will use for the lead-in text when assert_data() passes.
    """,
            validator=cf.is_instance_factory(str),
        )

    if "pass_message_bg_color" in option_keys or options == None:
        _register_option(
            name="pass_message_bg_color",
            default_value="green",
            description="""
    : str
    The background color that Pandas Checks will use for the lead-in text when assert_data() passes.
    """,
            validator=cf.is_instance_factory(str),
        )


# -----------------------
# General options
# -----------------------
def describe_options() -> None:
    """Prints all global options for Pandas Checks, their default values, and current values.

    Returns:
        None
    """
    for option in pd._config.config._select_options("pdchecks"):
        print()
        pd.describe_option(option)


def set_mode(enable_checks: bool, enable_asserts: bool) -> None:
    """Configures the operation mode for Pandas Checks globally.

    Args:
        enable_checks: Whether to run any Pandas Checks methods globally. Does not affect .check.assert_data().
        enable_asserts: Whether to run calls to .check.assert_data() globally.

    Returns:
        None
    """
    _set_option("enable_checks", enable_checks)
    _set_option("enable_asserts", enable_asserts)


def get_mode() -> Dict[str, bool]:
    """Returns whether Pandas Checks is currently running checks and assertions.

    Returns:
        A dictionary containing the current settings.
    """
    return {
        "enable_checks": pd.get_option("pdchecks.enable_checks"),
        "enable_asserts": pd.get_option("pdchecks.enable_asserts"),
    }


def enable_checks(enable_asserts: bool = True) -> None:
    """Turns on Pandas Checks globally. Subsequent calls to .check methods will be run.

    Args:
        enable_asserts: Whether to also enable or disable check.assert_data().

    Returns:
        None
    """
    set_mode(enable_checks=True, enable_asserts=enable_asserts)


def disable_checks(enable_asserts: bool = True) -> None:
    """Turns off all calls to Pandas Checks methods and optionally enables or disables check.assert_data(). Does not modify the DataFrame itself.

    If this function is called, subequent calls to .check functions will not be run.

    Typically used to
        1) Globally switch off Pandas Checks, such as during production. or
        2) Temporarily switch off Pandas Checks, such as for a stable part of a notebook.

    Args:
        enable_asserts: Whether to also run calls to Pandas Checks .check.assert_data()

    Returns:
        None
    """
    set_mode(enable_checks=False, enable_asserts=enable_asserts)


def _initialize_options() -> None:
    """Initializes (or resets) all Pandas Checks options to their default values.

    Returns:
        None

    Note:
        We separate this function from _initialize_format_options() so user can reset just formatting if desired without changing mode
    """

    # Register default mode options
    _register_option(
        name="enable_checks",
        default_value=True,
        description="""
    : bool
    Global setting for Pandas Checks to run checks and report all results.
    Set to False to disable checks and reporting, such as in a production environment.

    This option also enables/disables the timer functions.

    This option does not affect .check.assert_data(). Use separate option: `pdchecks.enable_asserts`
    """,
        validator=cf.is_instance_factory(bool),
    )
    _register_option(
        name="enable_asserts",
        default_value=True,
        description="""
    : bool
    Global setting for Pandas Checks to run .check.assert_data() methods. Set to False to disable assertions
    """,
        validator=cf.is_instance_factory(bool),
    )
    # Register default format options
    _initialize_format_options()
