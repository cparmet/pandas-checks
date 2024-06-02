from inspect import getsourcelines
from IPython.display import display
import pandas as pd
import pandas._config.config as cf
from pandas.core.groupby.groupby import DataError
from pandas.core.config_init import is_terminal
from pandas._config.config import is_instance_factory, is_nonnegative_int
from termcolor import colored
from time import time
import numpy as np

# Public functions
def start_timer(verbose=False):
    """
    TODO: Ideally we wouldn't use pandas config to store the start time.
    See if there's a better way store variables that will persist across Pandas method chains.
    They return newly initialized DataFrames at each method which reset all of a DataFrame's attributes.
    And we want to avoid global variables in the pandas_vet.py.
    """
    # Do we need to register option while setting it?
    if "vet.timer_start_time" not in pd._config.config._select_options("vet"):
        _register_vet_option(
            name="timer_start_time",
            default_value=time(),
            description="""
                : int
                Internal timer from the package pandas_vet. Used to create a global timer that will persist over method chains. Since Pandas returns a new, re-initialized DataFrame at each method to avoid mutating objects.
                """,
            validator=is_instance_factory(float)
        )
    # The option has already been registered. Re-set its value
    else:
        pd.set_option("vet.timer_start_time", time())
    if verbose:
        print("Started timer at:", pd.get_option("vet.timer_start_time"))

def print_time_elapsed(check_name="Time elapsed", units="auto"):
    """Reminder: If you change default arg values, change in .check.print_time_elapsed too"""
    start = pd.get_option("vet.timer_start_time")
    if start==np.nan:
        print("Timer hasn't been started. Call .check.start_time() before .check.get_time_elapsed()")
    elapsed = time() - start
    if units=="auto":
        if elapsed>60:
            units="minutes"
        elif elapsed>60*60:
            units="hours"
        else:
            units="seconds"
    if units=="minutes":
        elapsed/=60
    elif units=="hours":
        elapsed/=60*60
    elif units!="seconds":
        raise ValueError(f"Unexpected value for argument `units`: {units}")
    print(check_name + ": " if check_name else "", elapsed, units)

# Private functions
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
            validator=is_nonnegative_int
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
            validator=is_instance_factory(dict)
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
                    validator=is_instance_factory(str)
                )

def _format_success_message(message):
    return colored(message, pd.get_option("vet.success_text_fg_color"), pd.get_option("vet.success_text_bg_color"))

def _format_fail_message(message):
    return colored(message, pd.get_option("vet.fail_text_fg_color"), pd.get_option("vet.fail_text_bg_color"))

def _lambda_to_string(lambda_func):
    """TODO: This still returns all arguments to the calling function. They get entangled with the argument when it's a lambda function. Try other ways to get just the argument we want"""
    return (
        ''.join(
            getsourcelines(lambda_func)
            [0]
            )
        .lstrip(" .")
    )

def _modify_data(data, fn=lambda df: df, subset=None):
    """Select columna and apply user's arbitrary modifications to a data object.

    `data` may a Pandas DataFrame, Series, string, or other variable

    fn may be a lambda function or a string describing an operation that can be performed with 'eval()'
    
    """
    if callable(fn):
        data = fn(data)
    elif isinstance(fn, str):
        data = eval(fn, {}, {"df": data})
    else:
        raise TypeError(f"Argument `fn` is of unexpected type {type(fn)}")
    return data[subset] if subset else data

def _get_vet_table_styles():
    """Return empty list when all registered styles are {}"""
    return (
        [pd.get_option("vet.table_cell_hover_style")] if pd.get_option("vet.table_cell_hover_style") else []
    )

def _display_check(data, name=None):
    """ Behave differently if we're in an IPython interactive session / Jupyter nobteook"""
    try:
        print()
        if isinstance(data, (int, np.int8, np.int32, np.int64, str, float, np.float16, np.float32, np.float64, list, dict, tuple)):
            print(f"{name}:" if name else "",
                  data
                  ) # Print check name and result in one line
        elif not is_terminal():
            if isinstance(data, pd.DataFrame):
                display(
                    data
                    .style.set_caption(name if name else "") # Add check name to dataframe
                    .set_table_styles(_get_vet_table_styles())
                    .format(precision=pd.get_option("vet.precision"))
                    ) 
            elif isinstance(data, pd.Series):
                display(
                    pd.DataFrame(data)
                    .style.set_caption(name if name else "")
                    .set_table_styles(_get_vet_table_styles())
                    .format(precision=pd.get_option("vet.precision"))
                    ) # Add check name as column head
            else: # Print check name and data on separate lines
                if name: 
                    print(name)
                display(data) # Use IPython rendering
        else: # We're in a Terminal, like running a .py script, can't display Styled tables or use IPython rendering
            # Print check name and data on separate lines
            if name: 
                print(name)
            print(data)
    except TypeError:
        raise TypeError(f"Can't _display_data object of type {type(data)} in this environment.")

def _check_data(data, check_fn=lambda df: df, modify_fn=lambda df: df, subset=None, check_name=None, **kwargs):
    return (
        _display_check( # 3. Report the result
            check_fn(   # 2. After applying the method's operation to the data, like value_counts() or dtypes. May return a DF, an int, etc
                _modify_data(data, fn=modify_fn, subset=subset)   # 1. After first applying user's modifications to the data before checking it
            ),
            name=check_name if check_name else subset)
    )

## Public methods added to Pandas DataFrame
@pd.api.extensions.register_dataframe_accessor("check")
class DataFrameVet:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def set_format(self, **kwargs):
        for arg, value in kwargs.items():
            vet_option = arg if arg.startswith("vet.") else "vet." + arg # Fully qualified
            print(arg, value, vet_option)
            if vet_option in pd._config.config._select_options("vet"):
                print("set_option")
                pd.set_option(vet_option, value)
            else:
                raise AttributeError(f"No Pandas Vet option for {vet_option}. Available options: {pd._config.config._select_options('vet')}")
        return self._obj

    def reset_format(self):
        """Re-initilaize all Pandas Vet options for formatting"""
        _initialize_format_options()
        return self._obj

    def assert_data(
            self,
            condition,
            subset=None,
            exception_class=DataError,
            pass_message=" ✔️ Assertion passed ",
            fail_message=" ㄨ Assertion failed ",
            raise_exception=True,
            verbose=False
            ):
        data = self._obj[subset] if subset else self._obj
        if callable(condition):
            result = condition(data)
            condition_str = _lambda_to_string(condition)
        elif isinstance(condition, str):
            result = eval(condition_str:=condition, {}, {"df": data})
        else:
            raise TypeError(f"Argument `condition` is of unexpected type {type(condition)}")
        if not result:
            if raise_exception:
                raise exception_class(f"{fail_message}: {condition_str}") 
            else:
                print(f"{_format_fail_message(fail_message)}: {condition_str}")
        if verbose:
            print(f"{_format_success_message(pass_message)}: {condition_str}")
        return self._obj

    def describe(self, fn=lambda df: df, subset=None, check_name=None):
        _check_data(self._obj, check_fn=lambda df: df.describe(), modify_fn=fn, subset=subset, check_name=check_name)
        return self._obj

    def dtypes(self, fn=lambda df: df, subset=None, check_name='Data types'):
        _check_data(self._obj, check_fn=lambda df: df.dtypes, modify_fn=fn, subset=subset, check_name=check_name)
        return self._obj

    def evaluate(self, fn=lambda df: df, subset=None, check_name=None):
        _check_data(self._obj, modify_fn=fn, subset=subset, check_name=check_name)
        return self._obj
    
    def head(self, n=5, fn=lambda df: df, subset=None, check_name=None):
        _check_data(
            self._obj,
            check_fn=lambda df: df.head(n),
            modify_fn=fn,
            subset=subset,
            check_name=check_name if check_name else f"First {n} rows"
            )
        return self._obj

    def hist(self, fn=lambda df: df, subset=None):
        _ = (
            _modify_data(self._obj, fn, subset)
            .hist()
        )
        return self._obj

    def info(self, fn=lambda df: df, subset=None, check_name='Info'):
        """Don't use display or check_name comes below report """
        print()
        print(check_name)
        (
            _modify_data(self._obj, fn, subset)
            .info() 
        )
        return self._obj
    
    def memory_usage(self, fn=lambda df:df, subset=None, check_name='Memory usage'):
        _check_data(
            self._obj,
            check_fn=lambda df: df.memory_usage(),
            modify_fn=fn,
            subset=subset,
            check_name=check_name
            )
        return self._obj
        
    def ncols(self, fn=lambda df: df, subset=None, check_name='Columns'):
        _check_data(
            self._obj,
            check_fn=lambda df: df.shape[1],
            modify_fn=fn,
            subset=subset,
            check_name=check_name
            )
        return self._obj

    def ndups(self, fn=lambda df: df, subset=None, check_name=None):
        """TODO: add kwargs like subset"""
        _check_data(
            self._obj,
            check_fn=lambda df: df.duplicated().sum(),
            modify_fn=fn,
            subset=subset,
            check_name=check_name if check_name else f'Rows with duplication in {subset}' if subset else 'Duplicated rows')
        return self._obj

    def nnulls(self, fn=lambda df: df, subset=None, by_column=True, check_name=None):
        """TODO: add kwargs like subset
        by_column = False to count rows that have any NaNs in any columns
        """
        print()
        data = _modify_data(self._obj, fn, subset)
        na_counts = data.isna().any(axis=1).sum() if isinstance(data, pd.DataFrame) and not by_column else data.isna().sum()
        if not check_name:
            if isinstance(na_counts, (pd.DataFrame, pd.Series)): # Report result as a pandas object
                _check_data(na_counts, check_name=f'Rows with NaNs in {subset}' if subset else 'Rows with NaNs')
            else: # Report on one line
                print(
                    (f'Rows with NA in {subset}: ' if subset else 'Rows with NA: ')
                    + f"{na_counts} out of {data.shape[0]}" 
                )  
        else:
            print(f"{check_name}: {na_counts}")
        return self._obj

    def nrows(self, fn=lambda df: df, subset=None, check_name='Rows'):
        _check_data(
            self._obj,
            check_fn=lambda df: df.shape[0],
            modify_fn=fn,
            subset=subset,
            check_name=check_name
            )
        return self._obj

    def nunique(self, column, fn=lambda df: df, check_name=None):
        _check_data(
            self._obj,
            check_fn=lambda df: df.nunique(),
            modify_fn=fn,
            subset=column,
            check_name=check_name if check_name else f"Unique values in {column}"
            )
        return self._obj

    def plot(self, fn=lambda df: df, subset=None, check_name=None):
        _ = (
            _modify_data(self._obj, fn, subset)
            .plot(title=check_name)
        )
        return self._obj
    
    def print(self, text=None, fn=lambda df: df, subset=None, check_name=None, max_rows=10):
        _check_data(
            text if text else self._obj,
            check_fn=lambda data: data if text else data.head(max_rows),
            modify_fn=fn,
            subset=subset,
            check_name=check_name
            )
        return self._obj
    
    def shape(self, fn=lambda df: df, subset=None, check_name='Shape'):
        """See nrows, ncols"""
        _check_data(self._obj, check_fn=lambda df: df.shape, modify_fn=fn, subset=subset, check_name=check_name)
        return self._obj

    def start_timer(self, verbose=False):
        start_timer(verbose) # Call the public function
        return self._obj

    def tail(self, n=5, fn=lambda df: df, subset=None, check_name=None):            
        _check_data(
            self._obj,
            check_fn=lambda df: df.tail(n),
            modify_fn=fn,
            subset=subset,
            check_name=check_name if check_name else f"Last {n} rows"
            )
        return self._obj
    
    def print_time_elapsed(self, check_name="Time elapsed", units="auto"):
        print_time_elapsed(check_name=check_name, units=units) # Call the public function
        return self._obj

    def unique(self, column, fn=lambda df: df, check_name=None):
        _check_data(
            self._obj,
            check_fn=lambda df: df.unique().tolist(),
            modify_fn=fn,
            subset=column,
            check_name=check_name if check_name else f"Unique values of {column}"
            )
        return self._obj

    def value_counts(self, column, max_rows=10, fn=lambda df: df, check_name=None):
        check_name = check_name if check_name else f"Value counts, first {max_rows} values" if max_rows else f"Value counts"
        _check_data(
            self._obj,
            check_fn=lambda df: df.value_counts().head(max_rows),
            modify_fn=fn,
            subset=column,
            check_name=check_name
            )
        return self._obj

    def write(self, path, fn=lambda df: df, subset=None, verbose=False):
        data = _modify_data(self._obj, fn, subset)
        if path.endswith(".xls") or path.endswith(".xlsx"):
            data.to_excel(path)
        elif path.endswith(".csv"):
            data.to_csv(path)
        elif path.endswith(".parquet"):
            data.to_parquet(path)
        else:
            raise AttributeError(f"Can't write data to file. Unknown file extension in: {path}. ")
        if verbose:
            print("Wrote file {path}")
        return self._obj


# Initialize configuration
_initialize_format_options()