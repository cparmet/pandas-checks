from inspect import getsourcelines

import pandas as pd


def _in_terminal():
    return pd.core.config_init.is_terminal()


def _lambda_to_string(lambda_func):
    """TODO: This still returns all arguments to the calling function. They get entangled with the argument when it's a lambda function. Try other ways to get just the argument we want"""
    return "".join(getsourcelines(lambda_func)[0]).lstrip(" .")
