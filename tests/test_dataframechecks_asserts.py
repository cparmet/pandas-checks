from datetime import datetime, timedelta

import numpy as np
import pytest
from pandas.core.groupby.groupby import DataError

import pandas_checks  # Install the .check methods


def test_DataFrameChecks_assert_data_pass(iris):
    # Shouldn't raise an exception
    iris.check.assert_data(
        condition=lambda df: df.sum() > 0,  # DF because we apply subset after.
        subset="sepal_length",  # This is atypical usage, but want to test the args work nonetheless
        raise_exception=True,
        exception_to_raise=ValueError,
    )


def test_DataFrameChecks_assert_data_fail(iris):
    with pytest.raises(ValueError):
        assert iris.check.assert_data(
            condition=lambda df: df["sepal_length"].sum() < 0,
            raise_exception=True,
            exception_to_raise=ValueError,
        )


def test_DataFrameChecks_assert_data_custom_exception_fail(iris):
    with pytest.raises(ValueError):
        assert iris.check.assert_data(
            condition=lambda df: df["sepal_length"].sum() < 0,
            raise_exception=True,
            exception_to_raise=ValueError,
        )


def test_DataFrameChecks_assert_datetime_fail(iris):
    with pytest.raises(TypeError):
        assert iris.assign(
            mixed_types=lambda df: df["sepal_length"].replace(5.1, "string")
        ).check.assert_datetime(subset=["mixed_types"])


def test_DataFrameChecks_assert_datetime_pass(iris):
    (
        iris.assign(datetime_col=datetime(2020, 1, 1)).check.assert_datetime(
            subset="datetime_col"
        )
    )


def test_DataFrameChecks_assert_float_fail(iris):
    with pytest.raises(TypeError):
        assert iris.check.assert_float(subset=["species"])


def test_DataFrameChecks_assert_float_pass(iris):
    (iris.check.assert_float(subset=["sepal_length"]))


def test_DataFrameChecks_assert_greater_than_fail(iris):
    with pytest.raises(DataError):
        assert iris.check.assert_greater_than(10, subset=["sepal_length"])


def test_DataFrameChecks_assert_greater_than_pass(iris):
    (iris.check.assert_greater_than(-1, subset=["sepal_length"]))


def test_DataFrameChecks_assert_greater_than_str_fail(iris):
    with pytest.raises(DataError):
        assert iris.check.assert_greater_than("z", subset=["species"])


def test_DataFrameChecks_assert_greater_than_equal_to_fail(iris):
    with pytest.raises(DataError):
        assert iris.assign(int_col=4).check.assert_greater_than(
            4, or_equal_to=False, subset=["int_col"]
        )


def test_DataFrameChecks_assert_greater_than_datetime_fail(iris):
    with pytest.raises(DataError):
        assert iris.assign(datetime_col=datetime(2020, 1, 1)).check.assert_greater_than(
            datetime(2025, 1, 1), subset="datetime_col"
        )


def test_DataFrameChecks_assert_greater_than_datetime_pass(iris):
    (
        iris.assign(datetime_col=datetime(2020, 1, 1)).check.assert_greater_than(
            datetime(1901, 1, 1), subset="datetime_col"
        )
    )


def test_DataFrameChecks_assert_int_fail(iris):
    with pytest.raises(TypeError):
        assert iris.check.assert_int(subset=["species"])


def test_DataFrameChecks_assert_int_pass(iris):
    (iris.assign(int_col=4).check.assert_int(subset=["int_col"]))


def test_DataFrameChecks_assert_less_than_fail(iris):
    with pytest.raises(DataError):
        assert iris.check.assert_less_than(-0.01, subset=["sepal_length"])


def test_DataFrameChecks_assert_less_than_pass(iris):
    (iris.check.assert_less_than(1001, subset=["sepal_length"]))


def test_DataFrameChecks_assert_less_than_str_fail(iris):
    with pytest.raises(DataError):
        assert iris.check.assert_less_than("a", subset=["species"])


def test_DataFrameChecks_assert_less_than_equal_to_fail(iris):
    with pytest.raises(DataError):
        assert iris.assign(int_col=4).check.assert_less_than(
            4, or_equal_to=False, subset=["int_col"]
        )


def test_DataFrameChecks_assert_less_than_datetime_fail(iris):
    with pytest.raises(DataError):
        assert iris.assign(datetime_col=datetime(2020, 1, 1)).check.assert_less_than(
            datetime(1901, 1, 1), subset="datetime_col"
        )


def test_DataFrameChecks_assert_less_than_datetime_pass(iris):
    (
        iris.assign(datetime_col=datetime(2020, 1, 1)).check.assert_less_than(
            datetime(2025, 1, 1), subset="datetime_col"
        )
    )


def test_DataFrameChecks_assert_negative_fail(iris):
    with pytest.raises(DataError):
        assert iris.check.assert_negative(subset=["sepal_width", "petal_width"])


def test_DataFrameChecks_assert_negative_pass(iris):
    (iris.assign(all_negative=-1.4).check.assert_negative(subset=["all_negative"]))


def test_DataFrameChecks_assert_negative_one_null_fail(iris):
    with pytest.raises(DataError):
        assert iris.assign(
            one_null=lambda df: -df["sepal_length"].replace(5.1, np.nan)
        ).check.assert_negative(subset=["one_null"])


def test_DataFrameChecks_assert_negative_one_null_pass(iris):
    """Ignore nulls"""
    (
        iris.assign(
            one_null=lambda df: -df["sepal_length"].replace(5.1, np.nan)
        ).check.assert_negative(assert_not_null=False, subset=["one_null"])
    )


def test_DataFrameChecks_assert_not_null_fail(iris):
    with pytest.raises(DataError):
        assert iris.assign(
            one_null=lambda df: df["sepal_length"].replace(5.1, np.nan)
        ).check.assert_not_null(subset=["one_null"])


def test_DataFrameChecks_assert_not_null_pass(iris):
    (iris.check.assert_not_null(subset=["species"]))


def test_DataFrameChecks_assert_null_fail(iris):
    with pytest.raises(DataError):
        assert iris.check.assert_null(subset=["species"])


def test_DataFrameChecks_assert_null_one_null_fail(iris):
    with pytest.raises(DataError):
        assert iris.assign(
            one_null=lambda df: df["sepal_length"].replace(5.1, np.nan)
        ).check.assert_null(subset=["one_null"])


def test_DataFrameChecks_assert_null_pass(iris):
    (iris.assign(all_nulls=np.nan).check.assert_null(subset=["all_nulls"]))


def test_DataFrameChecks_assert_positive_pass(iris):
    (iris.check.assert_positive(subset=["sepal_width"]))


def test_DataFrameChecks_assert_positive_fail(iris):
    with pytest.raises(DataError):
        assert iris.assign(all_negative=-1.4).check.assert_positive(
            subset=["all_negative"]
        )


def test_DataFrameChecks_assert_positive_one_null_fail(iris):
    with pytest.raises(DataError):
        assert iris.assign(
            one_null=lambda df: df["sepal_length"].replace(5.1, np.nan)
        ).check.assert_positive(subset=["one_null"])


def test_DataFrameChecks_assert_positive_one_null_pass(iris):
    """Ignore nulls"""
    (
        iris.assign(
            one_null=lambda df: df["sepal_length"].replace(5.1, np.nan)
        ).check.assert_positive(assert_not_null=False, subset=["one_null"])
    )


def test_DataFrameChecks_assert_str_pass(iris):
    (iris.check.assert_str(subset=["species"]))


def test_DataFrameChecks_assert_int_fail(iris):
    with pytest.raises(TypeError):
        assert iris.check.assert_str(subset=["sepal_width"])


def test_DataFrameChecks_assert_timedelta_pass(iris):
    (
        iris.assign(timedelta_col=timedelta(days=1)).check.assert_timedelta(
            subset=["timedelta_col"]
        )
    )


def test_DataFrameChecks_assert_timedelta_fail(iris):
    with pytest.raises(TypeError):
        assert iris.assign(
            mixed_types_timedelta=lambda df: df["sepal_length"].replace(
                5.1, timedelta(days=1)
            )
        ).check.assert_timedelta(subset=["mixed_types_timedelta"])


def test_DataFrameChecks_assert_type_pass(iris):
    (iris.check.assert_type(float, subset=["sepal_length"]))


def test_DataFrameChecks_assert_type_fail(iris):
    with pytest.raises(TypeError):
        assert iris.check.assert_type(str, subset=["sepal_length", "petal_width"])


def test_DataFrameChecks_assert_type_mixed_fail(iris):
    with pytest.raises(TypeError):
        assert iris.assign(
            mixed_types=lambda df: df["sepal_length"].replace(5.1, "string")
        ).check.assert_type(float, subset=["mixed_types"])


def test_DataFrameChecks_assert_unique_pass(iris):
    (
        iris.assign(unique_col=range(0, iris.shape[0])).check.assert_unique(
            subset=["unique_col"]
        )
    )


def test_DataFrameChecks_assert_unique_fail(iris):
    with pytest.raises(DataError):
        assert iris.check.assert_unique(subset=["sepal_length"])


def test_DataFrameChecks_assert_unique_all_rows_pass(iris):
    (iris.drop_duplicates().check.assert_unique())
