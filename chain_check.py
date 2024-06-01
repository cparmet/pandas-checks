# from dill.source import getsource
from inspect import currentframe, getargvalues, getsourcelines
import pandas as pd
from pandas.core.groupby.groupby import DataError
from IPython.display import display
from time import time
import matplotlib # Must import for .plot()/.hist()
import numpy as np

# Certain functions requires:
# pip install Jinga2 # for table caption
# pip install openpyxl pyarrow  # For writing excel or parquet
# pip install matplotlib 
# dill

## Public functions
def start_timer():
    return time()

## Private functions
def _in_ipython():
    """Helper function to check if we're in IPython/Jupyter or a regular .py script"""
    try:
        # If get_ipython() is defined, it's an interactive environment
        return get_ipython() is not None
    except NameError:
        # If get_ipython() is not defined, it's a regular .py script
        return False

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

def _display_check(data, name=None, precision=2):
    """ Behave differently if we're in an IPython interactive session / Jupyter nobteook"""
    try:
        print()
        if isinstance(data, (int, np.int8, np.int32, np.int64, str, float, np.float16, np.float32, np.float64, list, dict, tuple)):
            print(f"{name}:" if name else "",
                  data
                  ) # Print check name and result in one line
        elif _in_ipython():  
            if isinstance(data, pd.DataFrame):
                display(
                    data
                    .style.set_caption(name if name else "") # Add check name to dataframe
                    .format(precision=precision)
                    ) 
            elif isinstance(data, pd.Series):
                display(
                    pd.DataFrame(data)
                    .style.set_caption(name if name else "")
                    .format(precision=precision)
                    ) # Add check name as column head
            else: # Print check name and data on separate lines
                if name: 
                    print(name)
                display(data) # Use IPython rendering
        else: # We're in a .py script, can't display Styled tables or use IPython rendering
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
            name=check_name if check_name else subset,
            precision= kwargs.get("precision", 2)
            )
    )

## Public methods added to Pandas DataFrame
@pd.api.extensions.register_dataframe_accessor("check")
class ChainCheckDataFrame:

    def __init__(self, pandas_obj):
        self._obj = pandas_obj
    
    def assert_data(
            self,
            condition,
            subset=None,
            exception_class=DataError,
            pass_message='✅ Passed',
            fail_message='❌ Failed',
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
                print(f"{fail_message}: {condition_str}")
        if verbose:
            print(f"{pass_message}: {condition_str}")
        return self._obj

    def describe(self, fn=lambda df: df, subset=None, check_name=None, **kwargs):
        _check_data(self._obj, check_fn=lambda df: df.describe(), modify_fn=fn, subset=subset, check_name=check_name, **kwargs)
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

    def tail(self, n=5, fn=lambda df: df, subset=None, check_name=None):            
        _check_data(
            self._obj,
            check_fn=lambda df: df.tail(n),
            modify_fn=fn,
            subset=subset,
            check_name=check_name if check_name else f"Last {n} rows"
            )
        return self._obj
    
    def time_elapsed(self, start_time, check_name="Time elapsed", units="seconds"):
        elapsed = time() - start_time
        if units=="minutes":
            elapsed/=60
        elif units=="hours":
            elapsed/=60*60
        elif units!="seconds":
            raise ValueError(f"Unexpected value for argument `units`: {units}")
        print(check_name + ": " if check_name else "", elapsed, units)
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

if "__name__"=="__main__":
    print("hi")
    print(pd.DataFrame(data=[0,1,2]))