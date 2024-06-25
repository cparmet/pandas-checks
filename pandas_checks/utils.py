"""
Utility functions for the pandas_checks package.
"""
from datetime import datetime, timedelta
from inspect import getsourcelines
from typing import Any, Callable, Type, Union

import pandas as pd
from pandas.core.groupby.groupby import DataError

from .display import _display_line


def _lambda_to_string(lambda_func: Callable) -> str:
    """Create a string representation of a lambda function.

    Args:
        lambda_func: An arbitrary function in lambda form

    Returns:
        A string version of lambda_func

    Todo:
        This still returns all arguments to the calling function.
            They get entangled with the argument when it's a lambda function.
            Try other ways to get just the argument we want.
    """
    return "".join(getsourcelines(lambda_func)[0]).lstrip(" .")


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
                f"{fail_message}: Nulls present (to disable, pass `assert_not_null=False`)"
            )
        else:
            _display_line(
                lead_in=fail_message,
                line="Nulls present (to disable, pass `assert_not_null=False`)",
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


def _series_is_type(s: pd.Series, dtype: Type[Any]) -> bool:
    """Utility function to check if a series has an expected type.
    Includes special handling for strings, since 'object' type in Pandas
    may not mean a string"""
    if dtype in [str, "str"]:
        return pd.api.types.is_string_dtype(s)
    elif dtype in [datetime, "datetime", "date"]:
        return pd.api.types.is_datetime64_any_dtype(
            s
        ) or pd.api.types.is_datetime64tz_dtype(s)
    elif dtype in [timedelta, "timedelta"]:
        return pd.api.types.is_timedelta64_dtype(s)
    else:
        return s.dtypes == dtype


def _is_type(data: pd.DataFrame, dtype: Type[Any]) -> bool:
    """Utility function to check if a dataframe's columns or one series has an expected type.
    Includes special handling for strings, since 'object' type in Pandas
    may not mean a string"""
    if isinstance(data, pd.Series):
        return _series_is_type(data, dtype)
    return all([_series_is_type(data[col], dtype) for col in data.columns])
