"""Utilities for running Pandas Checks data checks."""

from typing import Any, Callable, List, Type, Union

import pandas as pd
from pandas.core.groupby.groupby import DataError

from .display import _display_check, _display_line
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


def _has_nulls(
    data: Union[pd.DataFrame, pd.Series],
    fail_message: str,
    raise_exception: bool = True,
    exception_to_raise: Type[BaseException] = DataError,
) -> bool:
    """Utility function to check for nulls as part of a larger check"""
    if isinstance(data, pd.DataFrame):
        has_nulls = data.isna().any().any()
    elif isinstance(data, pd.Series):
        has_nulls = data.isna().any()
    else:
        raise AttributeError(f"Unexpected data type in _has_nulls(): {type(data)}")

    if has_nulls:
        if raise_exception:
            raise exception_to_raise(
                f"{fail_message}: Nulls present (to disable, pass `assert_no_nulls=False`)"
            )
        else:
            _display_line(
                lead_in=fail_message,
                line="Nulls present (to disable, pass `assert_no_nulls=False`)",
                colors={
                    "lead_in_text_color": pd.get_option(
                        "pdchecks.fail_message_fg_color"
                    ),
                    "lead_in_background_color": pd.get_option(
                        "pdchecks.fail_message_bg_color"
                    ),
                },
            )
    return has_nulls
