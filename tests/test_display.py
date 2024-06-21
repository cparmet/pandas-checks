import pytest

import pandas_checks as pdc
from pandas_checks.display import (
    _display_line,
    _filter_emojis,
    _format_background_color,
    _lead_in,
    _warning,
)


def test_filter_emojis():
    original = "Hello 🐼"
    no_emojis = "Hello"
    pdc.set_format(use_emojis=True)
    assert _filter_emojis(original) == original
    pdc.set_format(use_emojis=False)
    assert _filter_emojis(original) == no_emojis
    pdc.set_format(use_emojis=True)  # Reset for later tests


@pytest.mark.parametrize(
    "color, expected",
    [
        ("red", "on_red"),
        ("on_green", "on_green"),
        (None, None),
    ],
)
def test_format_background_color(color, expected):
    assert _format_background_color(color) == expected


@pytest.mark.parametrize(
    "lead_in, foreground, background, expected",
    [
        (
            "Hello",
            "red",
            "green",
            "<span style='color:red; background-color:green'>Hello:</span>",
        ),
        (None, "red", "green", ""),
    ],
)
def test_lead_in(lead_in, foreground, background, expected):
    assert _lead_in(lead_in, foreground, background) == expected


def test_display_line(capsys):
    _display_line("Hello")
    assert capsys.readouterr().out == "\nHello\n"


def test_warning(capsys):
    _warning("Test warning", "🐼🩺 Pandas Checks warning", True)
    assert capsys.readouterr().out == f"\n🐼🩺 Pandas Checks warning: Test warning\n"
