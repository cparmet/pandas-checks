import pandas as pd
import pytest

import pandas_vet as pdv
from pandas_vet.run_checks import _apply_modifications, _check_data


def test_apply_modifications_lambda():
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    fn = lambda x: x.assign(C=x.A + x.B)
    result = _apply_modifications(df, fn)
    expected = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6], "C": [5, 7, 9]})
    pd.testing.assert_frame_equal(result, expected)


def test_apply_modifications_str():
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    fn = lambda df: df.assign(C=df.A + df.B)
    result = _apply_modifications(df, fn)
    expected = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6], "C": [5, 7, 9]})
    pd.testing.assert_frame_equal(result, expected)


def test_apply_modifications_subset():
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6], "C": [7, 8, 9]})
    fn = lambda x: x
    subset = ["A", "C"]
    result = _apply_modifications(df, fn, subset)
    expected = pd.DataFrame({"A": [1, 2, 3], "C": [7, 8, 9]})
    pd.testing.assert_frame_equal(result, expected)


def test_apply_modifications_invalid_fn():
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    fn = 123
    with pytest.raises(TypeError):
        _apply_modifications(df, fn)


def test_check_data_enable_checks(capsys):
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    check_fn = lambda x: x.dtypes
    modify_fn = lambda x: x
    subset = None
    check_name = "Test Check"
    pdv.enable_checks()
    _check_data(df, check_fn, modify_fn, subset, check_name)
    assert "Test Check" in capsys.readouterr().out  # Partial check


def test_check_data_disable_checks(capsys):
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    check_fn = lambda x: x.dtypes
    modify_fn = lambda x: x
    subset = None
    check_name = "Test Check"
    pdv.disable_checks()
    _check_data(df, check_fn, modify_fn, subset, check_name)
    assert capsys.readouterr().out == ""
    pdv.enable_checks()  # Reset
