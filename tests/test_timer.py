import pytest

from pandas_vet.timer import print_time_elapsed, start_timer


def test_start_timer_returns_time():
    start_time = start_timer(verbose=True)
    assert isinstance(start_time, float)
    assert start_time > 0


def test_print_time_elapsed_invalid_units():
    with pytest.raises(ValueError):
        print_time_elapsed(1000.0, units="invalid")
