"""Utilities for running Pandas Vet data checks."""

from typing import Any, Callable, List, Union

import pandas as pd

from .display import _display_check
from .options import get_mode


def _apply_modifications(
    data: Any,
    fn: Union[Callable, Any] = lambda df: df,
    subset: Union[str, List, None] = None,
) -> Any:
    """Applies user's modifications to a data object.

    Args:
        data: May be any Pandas DataFrame, Series, string, or other variable
        fn: May be a lambda function or a string describing an operation that can be performed with 'eval()'
        subset: Columns to subset after applying modifications

    Returns:
        Modified and optionally subsetted data object.  If all arguments are defaults, data is returned unchanged.
    """
    if callable(fn):
        data = fn(data)
    elif isinstance(fn, str):
        data = eval(fn, {}, {"df": data})
    else:
        raise TypeError(f"Argument `fn` is of unexpected type {type(fn)}")
    return data[subset] if subset else data


def _check_data(
    data: Any,
    check_fn: Callable = lambda df: df,
    modify_fn: Union[Callable, str] = lambda df: df,
    subset: Union[str, List, None] = None,
    check_name: Union[str, None] = None,
) -> None:
    """Runs a selected Pandas Vet check on a data object

    Args:
        data: A Pandas DataFrame, Series, string, or other variable
        check_fn: Function to apply to data for checking. For example if we're running .check.value_counts(), this function would appply the Pandas value_counts() method
        modify_fn: Optional function or string to modify data _before_ checking
        subset: Optional list of columns or name of column to subset data before running check_fn
        check_name: Name to use when displaying check result

    Returns:
        None
    """
    if get_mode()["enable_checks"]:
        (
            # 3. Report the result
            _display_check(
                # 2. After applying the method's operation to the data,
                # like value_counts() or dtypes. May return a DF, an int, etc
                check_fn(
                    # 1. After first applying user's modifications to the data
                    # before checking it.
                    _apply_modifications(data, fn=modify_fn, subset=subset)
                ),
                name=check_name if check_name else str(subset) if subset else None,
            )
        )
