import pytest
from pytest_cases import parametrize_with_cases

from pandas_vet import disable_checks, enable_checks


# Helper function
def assert_equal_series(s1, s2):
    # Since NaN!=NaN, make them strings
    if not (s1.fillna("NULL").eq(s2.fillna("NULL")).all()):
        raise AssertionError


@parametrize_with_cases("df", cases=".datasets", prefix="df_")
@parametrize_with_cases("test_method", prefix="method_")
@pytest.mark.parametrize("enable_checks_flag", [True, False])
def test_seriesvet_methods_dont_change_series(
    df, test_method, tmp_path, enable_checks_flag
):
    enable_checks() if enable_checks_flag else disable_checks()
    for col in df.columns:
        assert_equal_series(
            s1=test_method(df[col], {"tmp_path": tmp_path}), s2=df[col]  # Args
        )
    if not enable_checks_flag:
        enable_checks()
