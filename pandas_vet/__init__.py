"""
This module imports and initializes Pandas Vet.
"""

# Select what functions are included in `from pandas_vet import *`
# i.e. don't expose DataFrameVet and SeriesVet, which aren't needed
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
# and select functions to expose in `from pandas_vet import ...`
from .DataFrameVet import DataFrameVet
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
from .SeriesVet import SeriesVet
from .timer import print_time_elapsed, start_timer

_initialize_options()
