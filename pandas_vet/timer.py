from time import time

import numpy as np
import pandas as pd
from pandas._config.config import is_instance_factory

from .display import _display_line
from .options import _register_option, get_mode


# Public functions
def start_timer(verbose=False):
    """
    TODO: Ideally we wouldn't use pandas config to store the start time.
    See if there's a better way store variables that will persist across Pandas method chains.
    They return newly initialized DataFrames at each method which reset all of a DataFrame's attributes.
    And we want to avoid global variables in the pandas_vet.py.
    """
    if not get_mode()["enable_checks"]:
        return None
    # Do we need to register option while setting it?
    if "vet.timer_start_time" not in pd._config.config._select_options("vet"):
        _register_option(
            name="timer_start_time",
            default_value=time(),
            description="""
                : int
                Internal timer from the package pandas_vet. Used to create a global timer that will persist over method chains. Since Pandas returns a new, re-initialized DataFrame at each method to avoid mutating objects.
                """,
            validator=is_instance_factory(float),
        )
    # The option has already been registered. Re-set its value
    else:
        pd.set_option("vet.timer_start_time", time())
    if verbose:
        _display_line(f"⏱️ Started timer at: {pd.get_option('vet.timer_start_time')}")


def print_time_elapsed(check_name="Time elapsed", units="auto"):
    """Reminder: If you change default arg values, change in .check.print_time_elapsed too"""
    if not get_mode()["enable_checks"]:
        return None
    start = pd.get_option("vet.timer_start_time")
    if start == np.nan:
        _display_line(
            "Timer hasn't been started. Call .check.start_time() before .check.get_time_elapsed()"
        )
    elapsed = time() - start
    if units == "auto":
        if elapsed > 60:
            units = "minutes"
        elif elapsed > 60 * 60:
            units = "hours"
        else:
            units = "seconds"
    if units == "minutes":
        elapsed /= 60
    elif units == "hours":
        elapsed /= 60 * 60
    elif units != "seconds":
        raise ValueError(f"Unexpected value for argument `units`: {units}")
    _display_line(
        f"{check_name + ':' if check_name else '⏱️ Time elapsed:'} {elapsed} {units}"
    )
