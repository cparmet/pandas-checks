import pandas as pd
import pandas._config.config as cf

# Public functions
def set_format(**kwargs):
    """Set PandasVet output format. Options include:"""
    for arg, value in kwargs.items():
        vet_option = arg if arg.startswith("vet.") else "vet." + arg # Fully qualified
        if vet_option in pd._config.config._select_options("vet"):
            pd.set_option(vet_option, value)
        else:
            raise AttributeError(f"No Pandas Vet option for {vet_option}. Available options: {pd._config.config._select_options('vet')}")

def reset_format():
    """Re-initilaize all Pandas Vet options for formatting"""
    _initialize_format_options()


# Private functions
def _get_vet_table_styles():
    """Return empty list when all registered styles are {}"""
    return (
        [pd.get_option("vet.table_cell_hover_style")] if pd.get_option("vet.table_cell_hover_style") else []
    )

def _register_vet_option(name, default_value, description, validator):
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

def _initialize_format_options(options=None):
    """Set up, or reset, Pandas Vet options
    None=initalize/reset all options"""
    option_keys = [option.replace("vet.", "") for option in options] if options else []
    if "precision" in option_keys or options==None:
        _register_vet_option(
            name="precision",
            default_value=2,
            description="""
                : int
                The floating point output precision of Pandas Vet outputs, in terms of number of places after the decimal, for regular formatting as well as scientific notation. Similar to ``precision`` in :meth:`numpy.set_printoptions`. Does not change precision of other Pandas methods. Use pd.set_option('display.precision',...) instead.
                """,
            validator=cf.is_nonnegative_int
            )
    if "table_cell_hover_style" in option_keys or options==None:
        _register_vet_option(
            name="table_cell_hover_style",
            default_value={
                'selector': 'td:hover',
                'props': [('background-color', '#2986cc')]
                        },
            description="""
                : int
                The background color to show when hovering over a Pandas Vet table`.
                """,
            validator=cf.is_instance_factory(dict)
            )
    if "use_emojis" in option_keys or options==None:
        _register_vet_option(
            name="use_emojis",
            default_value=False,
            description="""
                : int
                Whether Pandas Vet check_names should keep emojis. This includes default check_names from the factory and user-supplied check_names`.
                """,
            validator=cf.is_instance_factory(bool)
            )
    # Text color for failure and success messages
    for option, default in {
        "fail_text_fg_color": "white",
        "fail_text_bg_color": "on_red",
        "success_text_fg_color": "black",
        "success_text_bg_color": "on_green"
        }.items():
            if "option" in option_keys or options==None:
                _register_vet_option(
                    name=option,
                    default_value=default,
                    description=f"""
                        : str
                            Color of {"text" if "fg" in option else "background"} for Pandas Vet {option.split("_")[0]} messages.
                        """,
                    validator=cf.is_instance_factory(str)
                )
