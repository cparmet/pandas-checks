import pandas as pd
import pandas._config.config as cf


# -----------------------
# Helpers
# -----------------------
def _set_option(option, value):
        vet_option = option if option.startswith("vet.") else "vet." + option # Fully qualified
        if vet_option in pd._config.config._select_options("vet"):
            pd.set_option(vet_option, value)
        else:
            raise AttributeError(f"No Pandas Vet option for {vet_option}. Available options: {pd._config.config._select_options('vet')}")


def _register_option(name, default_value, description, validator):
    """Add a Pandas Vet option to the Pandas configuration.
    This method enables us to set global formatting for Vet checks
    and store variables that will persist across Pandas method chains
    which return newly initialized DataFrames at each method
    (resetting DataFrame's attributes)."""
    key_name = name if "vet." not in name else name.replace("vet,","") # If we passed vet.name, strip vet., since we'll be working in "vet" config namespace
    try: # See if this option is already registered
        pd.get_option(f"vet.{key_name}")
        # If so, reset its value
        pd.set_option(f"vet.{key_name}", default_value)
    except pd.errors.OptionError: # Register it!
        with cf.config_prefix("vet"):
            cf.register_option(
                key_name,
                default_value,
                description,validator
                )

# -----------------------
# Formatting
# -----------------------

def set_format(**kwargs):
    """Set PandasVet output format. Options include: ... """
    for arg, value in kwargs.items():
        _set_option(arg, value)

def reset_format():
    """Re-initilaize all Pandas Vet options for formatting"""
    _initialize_format_options()

def _initialize_format_options(options=None):
    """Set up or reset Pandas Vet options for formatting
    None=initalize/reset all options

    Separate from _initialize_options so user can reset just formatting if desired
    """
    option_keys = [option.replace("vet.", "") for option in options] if options else []
    if "precision" in option_keys or options==None:
        _register_option(
            name="precision",
            default_value=2,
            description="""
    : float
    The floating point output precision of Pandas Vet outputs, in terms of number of places after the decimal, for regular formatting as well as scientific notation. Similar to ``precision`` in :meth:`numpy.set_printoptions`. Does not change precision of other Pandas methods. Use pd.set_option('display.precision',...) instead.
    """,
            validator=cf.is_nonnegative_int
            )
    if "table_row_hover_style" in option_keys or options==None:
        _register_option(
            name="table_row_hover_style",
            default_value={
                'selector': 'tr:hover',
                'props': [('background-color', '#2986cc')]
                        },
            description="""
    : dict
    The background color to show when hovering over a Pandas Vet table`.
    """,
            validator=cf.is_instance_factory(dict)
            )
    if "use_emojis" in option_keys or options==None:
        _register_option(
            name="use_emojis",
            default_value=True,
            description="""
    : bool
    Whether Pandas Vet check_names should keep emojis. This includes default check_names from the factory and user-supplied check_names`.
    """,
            validator=cf.is_instance_factory(bool)
            )
    if "indent_table_terminal" in option_keys or options==None:
        _register_option(
            name="indent_table_terminal",
            default_value=4,
            description="""
    : int
    Number of spaces to indent Pandas Vet tables in terminal display.
    """,
            validator=cf.is_instance_factory(int)
            )
    if "indent_table_plot_ipython" in option_keys or options==None:
        _register_option(
            name="indent_table_plot_ipython",
            default_value=30,
            description="""
    : int
    Number of pixels to indent Pandas Vet tables or plots in IPython/Jupyter display.
    """,
            validator=cf.is_instance_factory(int)
            )
    # Text styling
    for option, default in {
        "check_text_tag": "h5",
        "table_title_tag": "h5",
        "plot_title_tag": "h5",
        "fail_text_fg_color": "white",
        "fail_text_bg_color": "red",
        "success_text_fg_color": "black",
        "success_text_bg_color": "green"
        }.items():
            if "option" in option_keys or options==None:
                _register_option(
                    name=option,
                    default_value=default,
                    description=f"""
    : str
    {"A single HTML tag (h1, h5, p, etc)" if "tag" in option else "Foreground color" if "fg" in option else "Background color"} for Pandas Vet {option.replace("_tag","").replace("_fg_color","").replace("_fg_color","")}.
    """,
                    validator=cf.is_instance_factory(str)
                )

# -----------------------
# General options
# -----------------------
def describe_options():
    """Print all global options for PandasVet, their default values, and current values.
    """
    for option in pd._config.config._select_options("vet"):
        print()
        pd.describe_option(option)

def set_mode(enable_checks, enable_asserts):
    _set_option("enable_checks", enable_checks)
    _set_option("enable_asserts", enable_asserts)

def get_mode():
    return {
        "enable_checks": pd.get_option("vet.enable_checks"),
        "enable_asserts": pd.get_option("vet.enable_asserts"),
    }

def enable_checks(enable_asserts=True):
    """Convenience function to enable checks +/- asserts"""
    set_mode(enable_checks=True, enable_asserts=enable_asserts)

def disable_checks(enable_asserts=True):
    """Convenience function to disable checks +/- asserts"""
    set_mode(enable_checks=False, enable_asserts=enable_asserts)

def _initialize_options():
    """Set up, or reset, Pandas Vet options
    NOTE: We separate this function from _initialize_format_options() so user can reset just formatting if desired"""

    # Register default mode options
    _register_option(
        name="enable_checks",
        default_value=True,
        description="""
    : bool
    Global setting for PandasVet to run checks and report all results.
    Set to False to disable checks and reporting, such as in a production environment.

    This option also enables/disables the timer functions.

    This option does not affect .check.assertion(). Use separate option: `vet.enable_asserts`
    """,
        validator=cf.is_instance_factory(bool)
    )
    _register_option(
        name="enable_asserts",
        default_value=True,
        description="""
    : bool
    Global setting for PandasVet to run .check.assertion() methods. Set to False to disable assertions
    """,
        validator=cf.is_instance_factory(bool)
    )
    # Register default format options
    _initialize_format_options()