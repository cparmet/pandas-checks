"""
Utility functions for the pandas_checks package.
"""
from inspect import getsourcelines
from typing import Callable

import pandas as pd


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
