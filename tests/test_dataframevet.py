import pandas as pd
import pytest
from pytest_cases import parametrize_with_cases

# from .conftest import DF_METHODS
from pandas_vet import disable_checks, enable_checks


# Helper function
def assert_equal_df(df1, df2):
    if df1.ne(df2).all().all():  # Reminder: NaN!=NaN
        raise AssertionError


@parametrize_with_cases("df", prefix="df_")
@parametrize_with_cases("test_method", prefix="method_")
@pytest.mark.parametrize("enable_checks_flag", [True, False])
def test_dataframevet_methods_dont_change_df(
    df, test_method, tmp_path, enable_checks_flag
):
    args = {
        "first_num_col": df.select_dtypes(include=["int64", "float64"]).columns[0],
        "tmp_path": tmp_path,
    }
    enable_checks() if enable_checks_flag else disable_checks()
    assert_equal_df(test_method(df, args), df)
