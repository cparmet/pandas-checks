"""
Provides a timer utility for tracking the elapsed time of steps within a Pandas method chain.

Note that these functions rely on the `vet.enable_checks` option being enabled in the Pandas configuration, as it is by default.
"""
from time import time
from typing import Union

import numpy as np

from .display import _display_line
from .options import get_mode


# Public functions
def start_timer(verbose: bool = False) -> float:
    """Starts a Pandas Vet stopwatch to measure run time between operations, such as steps in a Pandas method chain. Use print_elapsed_time() to get timings.

    Args:
        verbose: Whether to print a message that the timer has started.

    Returns:
        Timestamp as a float
    """
    if not get_mode()["enable_checks"]:
        return np.nan
    t = time()
    if verbose:
        _display_line(f"⏱️ Started timer at: {t}")
    return t


def print_time_elapsed(
    start_time: float, lead_in: Union[str, None] = "Time elapsed", units: str = "auto"
) -> None:
    """Displays the time elapsed since start_time.

    Args:
        start_time: The index time when the stopwatch started, which comes from the Pandas Vet start_timer()
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

    if get_mode()["enable_checks"]:
        if start_time == np.nan:
            _display_line("Timer hasn't been started. Call start_timer() first")
        elapsed = time() - start_time
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
