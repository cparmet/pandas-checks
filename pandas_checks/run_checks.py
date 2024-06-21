"""Utilities for running Pandas Checks data checks."""

from typing import Any, Callable, List, Union

import pandas as pd

from .display import _display_check
from .options import get_mode


def _apply_modifications(
    data: Any,
    fn: Callable = lambda df: df,
    subset: Union[str, List, None] = None,
) -> Any:
    """Applies user's modifications to a data object.

    Args:
        data: May be any Pandas DataFrame, Series, string, or other variable
        fn: An optional lambda function to modify `data`
        subset: Columns to subset after applying modifications

    Returns:
        Modified and optionally subsetted data object.  If all arguments are defaults, data is returned unchanged.
    """
    if not callable(fn):
        raise TypeError(
            f"Expected lambda function for argument `fn` (callable type), but received type {type(fn)}"
        )
    return fn(data)[subset] if subset else fn(data)


def _check_data(
    data: Any,
    check_fn: Callable = lambda df: df,
    modify_fn: Callable = lambda df: df,
    subset: Union[str, List, None] = None,
    check_name: Union[str, None] = None,
) -> None:
    """Runs a selected check on a data object

    Args:
        data: A Pandas DataFrame, Series, string, or other variable
        check_fn: Function to apply to data for checking. For example if we're running .check.value_counts(), this function would appply the Pandas value_counts() method
        modify_fn: Optional function to modify data _before_ checking
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
