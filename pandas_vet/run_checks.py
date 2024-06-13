from typing import Any, Callable, List, Union

import pandas as pd

from .display import _display_check
from .options import get_mode


def _modify_data(
    data: Any,
    fn: Union[Callable, Any] = lambda df: df,
    subset: Union[str, List, None] = None,
) -> Any:
    """Apply user's arbitrary modifications to a data object
    then subset the columns if requested.

    If all arguments are defaults, this function returns `data` unchanged.

    `data` may be any Pandas DataFrame, Series, string, or other variable

    `fn` may be a lambda function or a string describing an operation
    that can be performed with 'eval()'

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
    """`data` may be any Pandas DataFrame, Series, string, or other variable"""
    if get_mode()["enable_checks"]:
        (
            # 3. Report the result
            _display_check(
                # 2. After applying the method's operation to the data,
                # like value_counts() or dtypes. May return a DF, an int, etc
                check_fn(
                    # 1. After first applying user's modifications to the data
                    # before checking it.
                    _modify_data(data, fn=modify_fn, subset=subset)
                ),
                name=check_name if check_name else str(subset),
            )
        )
