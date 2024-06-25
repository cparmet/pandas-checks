from datetime import datetime, timedelta

import numpy as np
import pytest
from pandas.core.groupby.groupby import DataError

import pandas_checks  # Install the .check methods


def test_SeriesChecks_assert_data_pass(iris):
    # Shouldn't raise an exception
    (
        iris["sepal_length"].check.assert_data(
            condition=lambda s: s.sum() > 0,
            raise_exception=True,
            exception_to_raise=ValueError,
        )
    )


def test_SeriesChecks_assert_data_fail(iris):
    with pytest.raises(DataError):
        assert iris["sepal_length"].check.assert_data(
            condition=lambda s: s.sum() < 0,
            raise_exception=True,
        )


def test_SeriesChecks_assert_data_custom_exception_fail(iris):
    with pytest.raises(ValueError):
        assert iris["sepal_length"].check.assert_data(
            condition=lambda s: s.sum() < 0,
            raise_exception=True,
            exception_to_raise=ValueError,
        )


def test_SeriesChecks_assert_datetime_fail(iris):
    with pytest.raises(TypeError):
        assert iris.assign(
            mixed_types=lambda df: df["sepal_length"].replace(5.1, "string")
        )["mixed_types"].check.assert_datetime()


def test_SeriesChecks_assert_datetime_pass(iris):
    (
        iris.assign(datetime_col=datetime(2020, 1, 1))[
            "datetime_col"
        ].check.assert_datetime()
    )


def test_SeriesChecks_assert_float_fail(iris):
    with pytest.raises(TypeError):
        assert iris["species"].check.assert_float()


def test_SeriesChecks_assert_float_pass(iris):
    (iris["sepal_length"].check.assert_float())


def test_SeriesChecks_assert_greater_than_fail(iris):
    with pytest.raises(DataError):
        assert iris["sepal_length"].check.assert_greater_than(10)


def test_SeriesChecks_assert_greater_than_pass(iris):
    (iris["sepal_length"].check.assert_greater_than(-1, verbose=True))


def test_SeriesChecks_assert_greater_than_str_fail(iris):
    with pytest.raises(DataError):
        assert iris["species"].check.assert_greater_than("z")


def test_SeriesChecks_assert_greater_than_equal_to_fail(iris):
    with pytest.raises(DataError):
        assert iris.assign(int_col=4)["int_col"].check.assert_greater_than(
            4, or_equal_to=False
        )


def test_SeriesChecks_assert_greater_than_datetime_fail(iris):
    with pytest.raises(DataError):
        assert iris.assign(datetime_col=datetime(2020, 1, 1))[
            "datetime_col"
        ].check.assert_greater_than(datetime(2025, 1, 1))


def test_SeriesChecks_assert_greater_than_datetime_pass(iris):
    (
        iris.assign(datetime_col=datetime(2020, 1, 1))[
            "datetime_col"
        ].check.assert_greater_than(datetime(1901, 1, 1))
    )


def test_SeriesChecks_assert_int_fail(iris):
    with pytest.raises(TypeError):
        assert iris["species"].check.assert_int()


def test_SeriesChecks_assert_int_pass(iris):
    (iris.assign(int_col=4)["int_col"].check.assert_int())


def test_SeriesChecks_assert_less_than_fail(iris):
    with pytest.raises(DataError):
        assert iris["sepal_length"].check.assert_less_than(-0.01)


def test_SeriesChecks_assert_less_than_pass(iris):
    (iris["sepal_length"].check.assert_less_than(1001, verbose=True))


def test_SeriesChecks_assert_less_than_str_fail(iris):
    with pytest.raises(DataError):
        assert iris["species"].check.assert_less_than("a")


def test_SeriesChecks_assert_less_than_equal_to_fail(iris):
    with pytest.raises(DataError):
        assert iris.assign(int_col=4)["int_col"].check.assert_less_than(
            4, or_equal_to=False
        )


def test_SeriesChecks_assert_less_than_datetime_fail(iris):
    with pytest.raises(DataError):
        assert iris.assign(datetime_col=datetime(2020, 1, 1))[
            "datetime_col"
        ].check.assert_less_than(datetime(1901, 1, 1))


def test_SeriesChecks_assert_less_than_datetime_pass(iris):
    (
        iris.assign(datetime_col=datetime(2020, 1, 1))[
            "datetime_col"
        ].check.assert_less_than(
            datetime(2025, 1, 1),
        )
    )


def test_SeriesChecks_assert_negative_fail(iris):
    with pytest.raises(DataError):
        assert iris["sepal_width"].check.assert_negative()


def test_SeriesChecks_assert_negative_pass(iris):
    (iris.assign(all_negative=-1.4)["all_negative"].check.assert_negative())


def test_SeriesChecks_assert_negative_one_null_fail(iris):
    with pytest.raises(DataError):
        assert iris.assign(
            one_null=lambda df: -df["sepal_length"].replace(5.1, np.nan)
        )["one_null"].check.assert_negative()


def test_SeriesChecks_assert_negative_one_null_pass(iris):
    """Ignore nulls"""
    (
        iris.assign(one_null=lambda df: -df["sepal_length"].replace(5.1, np.nan))[
            "one_null"
        ].check.assert_negative(assert_no_nulls=False)
    )


def test_SeriesChecks_assert_no_nulls_fail(iris):
    with pytest.raises(DataError):
        assert iris.assign(one_null=lambda df: df["sepal_length"].replace(5.1, np.nan))[
            "one_null"
        ].check.assert_no_nulls()


def test_SeriesChecks_assert_no_nulls_pass(iris):
    (iris["species"].check.assert_no_nulls())


def test_SeriesChecks_assert_null_fail(iris):
    with pytest.raises(DataError):
        assert iris["species"].check.assert_null()


def test_SeriesChecks_assert_null_one_null_fail(iris):
    with pytest.raises(DataError):
        assert iris.assign(one_null=lambda df: df["sepal_length"].replace(5.1, np.nan))[
            "one_null"
        ].check.assert_null()


def test_SeriesChecks_assert_null_pass(iris):
    (iris.assign(all_nulls=np.nan)["all_nulls"].check.assert_null())


def test_SeriesChecks_assert_positive_pass(iris):
    (iris["sepal_width"].check.assert_positive())


def test_SeriesChecks_assert_positive_fail(iris):
    with pytest.raises(DataError):
        assert iris.assign(all_negative=-1.4)["all_negative"].check.assert_positive()


def test_SeriesChecks_assert_positive_one_null_fail(iris):
    with pytest.raises(DataError):
        assert iris.assign(one_null=lambda df: df["sepal_length"].replace(5.1, np.nan))[
            "one_null"
        ].check.assert_positive()


def test_SeriesChecks_assert_positive_one_null_pass(iris):
    """Ignore nulls"""
    (
        iris.assign(one_null=lambda df: df["sepal_length"].replace(5.1, np.nan))[
            "one_null"
        ].check.assert_positive(assert_no_nulls=False)
    )


def test_SeriesChecks_assert_str_pass(iris):
    (iris["species"].check.assert_str())


def test_SeriesChecks_assert_int_fail(iris):
    with pytest.raises(TypeError):
        assert iris["sepal_width"].check.assert_str()


def test_SeriesChecks_assert_timedelta_pass(iris):
    (
        iris.assign(timedelta_col=timedelta(days=1))[
            "timedelta_col"
        ].check.assert_timedelta()
    )


def test_SeriesChecks_assert_timedelta_fail(iris):
    with pytest.raises(TypeError):
        assert iris.assign(
            mixed_types_timedelta=lambda df: df["sepal_length"].replace(
                5.1, timedelta(days=1)
            )
        )["mixed_types_timedelta"].check.assert_timedelta()


def test_SeriesChecks_assert_type_pass(iris):
    (iris["sepal_length"].check.assert_type(float))


def test_SeriesChecks_assert_type_fail(iris):
    with pytest.raises(TypeError):
        assert iris["sepal_length"].check.assert_type(str)


def test_SeriesChecks_assert_type_mixed_fail(iris):
    with pytest.raises(TypeError):
        assert iris.assign(
            mixed_types=lambda df: df["sepal_length"].replace(5.1, "string")
        )["mixed_types"].check.assert_type(float)


def test_SeriesChecks_assert_unique_pass(iris):
    (
        iris.assign(unique_col=range(0, iris.shape[0]))[
            "unique_col"
        ].check.assert_unique()
    )


def test_SeriesChecks_assert_unique_fail(iris):
    with pytest.raises(DataError):
        assert iris["sepal_length"].check.assert_unique()
