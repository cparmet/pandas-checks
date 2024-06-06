from .display import (
    _get_vet_table_styles,
    _display_line,
    _display_table_title,
    _filter_emojis
)

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


def _display_check(data, name=None):
    """ Behave differently if we're in an IPython interactive session / Jupyter nobteook"""
    try:
        # Is it a one-liner result?
        if isinstance(data, (int, np.int8, np.int32, np.int64, str, float, np.float16, np.float32, np.float64, list, dict, tuple)):
            _display_line(f"{name}: {data}" if name else data) # Print check name and result in one line
        # Are we in IPython/Jupyter?
        elif not pd.core.config_init.is_terminal():
            # Is it a DF?
            if isinstance(data, pd.DataFrame):
                _display_table_title(name)
                display(
                    data
                    .style.set_table_styles(_get_vet_table_styles())
                    .format(precision=pd.get_option("vet.precision"))
                    ) 
            # Or a Series we should format as a DF?
            elif isinstance(data, pd.Series):
                _display_table_title(name)
                display(
                    pd.DataFrame(
                        # For Series based on some Pandas outputs like memory_usage(),
                        # don't show a column name of 0
                        data.rename(data.name if data.name!=0 and data.name!=None else "")
                        )
                    .style.set_table_styles(_get_vet_table_styles())
                    .format(precision=pd.get_option("vet.precision"))
                    ) # Add check name as column head
            # Otherwise, show check name and data on separate lines
            else:
                _display_line(name)
                display(data) # Use IPython rendering
        else: # We're in a Terminal, like running a .py script, can't display Styled tables or use IPython rendering
            # Print check name and data on separate lines
            if name: 
                print(_filter_emojis(name))
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

