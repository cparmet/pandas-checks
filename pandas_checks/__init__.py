"""
This module imports and initializes Pandas Checks.
"""

# Select what functions are included in `from pandas_checks import *`
# i.e. don't expose DataFrameChecks and SeriesChecks, which aren't needed
__all__ = [
    "_initialize_options",
    "describe_options",
    "disable_checks",
    "enable_checks",
    "get_mode",
    "print_time_elapsed",
    "reset_format",
    "set_format",
    "set_mode",
    "start_timer",
]

# Register our changes to the Pandas classes
# and select functions to expose in `from pandas_checks import ...`
from .DataFrameChecks import DataFrameChecks
from .options import (
    _initialize_options,
    describe_options,
    disable_checks,
    enable_checks,
    get_mode,
    reset_format,
    set_format,
    set_mode,
)
from .SeriesChecks import SeriesChecks
from .timer import print_time_elapsed, start_timer

_initialize_options()
