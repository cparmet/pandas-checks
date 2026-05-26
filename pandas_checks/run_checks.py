"""Utilities for running Pandas Checks data checks."""

from typing import Any, Callable, Union

import pandas as pd

from .display import _display_check
from .options import get_mode
from .utils import SubsetTypes


def _apply_modifications(
    data: Any,
    fn: Callable = lambda df: df,
    subset: SubsetTypes = None,
) -> Any:
    """Applies user's modifications to a data object.

    Args:
        data: May be any Pandas DataFrame, Series, string, or other variable
        fn: An optional lambda function to modify `data`
        subset: Optional column name or names to filter the data to. Applied after fn.

    Returns:
        Modified and optionally subsetted data object.  If all arguments are defaults, data is returned unchanged.
    """
    if not callable(fn):
        raise TypeError(
            f"Expected lambda function for argument `fn` (callable type), but received type {type(fn)}"
        )

    if isinstance(subset, list | tuple | set | pd.Index):
        # Reminder: We don't use Sequence because that would include str, and "" is a valid column name for `subset`
        if len(subset) == 0:
            raise ValueError(
                f"Pandas Checks received empty sequence for subset: {subset}"
            )

    return fn(data)[subset] if subset is not None else fn(data)


def _check_data(
    data: Any,
    check_fn: Callable = lambda df: df,
    modify_fn: Callable = lambda df: df,
    subset: SubsetTypes = None,
    msg: Union[str, None] = None,
) -> None:
    """Runs a selected check on a data object

    Args:
        data: A Pandas DataFrame, Series, string, or other variable
        check_fn: Function to apply to data for checking. For example if we're running .check.value_counts(), this function would appply the Pandas value_counts() method
        modify_fn: Optional function to modify data _before_ checking
        subset: Optional column name or names to select before running check_fn
        msg: Name to use when displaying check result

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
                name=msg
                if msg is not None
                else str(subset)
                if subset is not None
                else None,
            )
        )
