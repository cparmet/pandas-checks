from .utils import _filter_emojis
from IPython.display import display
import numpy as np
import pandas as pd

def _modify_data(data, fn=lambda df: df, subset=None):
    """Apply user's arbitrary modifications to a data object then subset the columns if requested.

    If all arguments are defaults, this function returns `data` unchanged.

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
            print(f"{name}: {data}" if name else data) # Print check name and result in one line
        elif not pd.core.config_init.is_terminal():
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
            name=_filter_emojis(check_name) if check_name else subset)
    )

