"""
Provides a timer utility for tracking the elapsed time of steps within a Pandas method chain.

Note that these functions rely on the `vet.enable_checks` option being enabled in the Pandas configuration, as it is by default.
"""
from time import time
from typing import Union

import numpy as np
import pandas as pd
from pandas._config.config import is_instance_factory

from .display import _display_line
from .options import _register_option, get_mode


# Public functions
def start_timer(verbose: bool = False) -> None:
    """Starts a Pandas Vet stopwatch to measure run time between operations, such as steps in a Pandas method chain. Use print_elapsed_time() to get timings.

    Args:
        verbose: Whether to print a message that the timer has started.

    Returns:
        None

    Todo:
        Ideally we wouldn't use pandas config to store the start time.
            See if there's a better way store variables that will persist across Pandas method chains.
            They return newly initialized DataFrames at each method which reset all of a DataFrame's attributes.
            And we want to avoid global variables in the pandas_vet.py, which could cause problems with shared context.
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


def print_time_elapsed(
    lead_in: Union[str, None] = "Time elapsed", units: str = "auto"
) -> None:
    """Displays the time elapsed since the Pandas Vet stopwatch was started with start_timer().

    Args:
        lead_in: Optional text to print before the elapsed time.
        units: The units in which to display the elapsed time. Can be "auto", "seconds", "minutes", or "hours". Defaults to "auto".

    Returns:
        None

    Raises:
        ValueError: If `units` is not one of "auto", "seconds", "minutes", or "hours".

    Note:
        If you change the default values for this function's argument,
        change them in `.check.print_time_elapsed` too in DataFrameVet and SeriesVet
        so they're exposed to the user.
    """

    if not get_mode()["enable_checks"]:
        return None
    start = pd.get_option("vet.timer_start_time")
    if start == np.nan:
        _display_line("Timer hasn't been started. Call start_timer() first")
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
        f"{lead_in + ':' if lead_in else '⏱️ Time elapsed:'} {elapsed} {units}"
    )
