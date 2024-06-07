import pandas as pd
import pandas._config.config as cf

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
    if "table_row_hover_style" in option_keys or options==None:
        _register_vet_option(
            name="table_row_hover_style",
            default_value={
                'selector': 'tr:hover',
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
            default_value=True,
            description="""
                : int
                Whether Pandas Vet check_names should keep emojis. This includes default check_names from the factory and user-supplied check_names`.
                """,
            validator=cf.is_instance_factory(bool)
            )
    if "indent_table_terminal" in option_keys or options==None:
        _register_vet_option(
            name="indent_table_terminal",
            default_value=4,
            description="""
                : int
                Number of spaces to indent Pandas Vet tables in terminal display.
                """,
            validator=cf.is_instance_factory(int)
            )
    # Text styling
    for option, default in {
        "check_text_tag": "h5",
        "table_title_tag": "h5",
        "plot_title_tag": "h5",
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
                        {"A single HTML tag (h1, h5, p, etc)" if "tag" in option else "Foreground color" if "fg" in option else "Background color"} for Pandas Vet {option.replace("_tag","").replace("_fg_color","").replace("_fg_color","")}.
                        """,
                    validator=cf.is_instance_factory(str)
                )
