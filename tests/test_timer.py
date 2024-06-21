import pytest

from pandas_checks.timer import print_time_elapsed, start_timer


def test_start_timer_returns_time():
    start_time = start_timer(verbose=True)
    assert isinstance(start_time, float)
    assert start_time > 0


@pytest.mark.parametrize(
    "units_outputcontains",
    (
        ("auto", "milliseconds"),
        ("milliseconds", "milliseconds"),
        ("ms", "ms"),
        ("seconds", "seconds"),
        ("s", "s"),
        ("minutes", "minutes"),
        ("m", "m"),
        ("hours", "hours"),
        ("h", "h"),
    ),
)
def test_print_time_elapsed_valid_units(units_outputcontains, capsys):
    """We can't test the actual timings, since runtimes vary. So we'll test units"""
    units = units_outputcontains[0]
    output_contains = units_outputcontains[1]
    print_time_elapsed(start_time=start_timer(), units=units)
    assert output_contains in capsys.readouterr().out


def test_print_time_elapsed_invalid_units():
    with pytest.raises(ValueError):
        print_time_elapsed(1000.0, units="parsecs")
