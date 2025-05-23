"""
This module installs Pandas Checks methods in the Pandas DataFrame class.

To use Pandas Checks, don't access anything in this module directly. Instead just run `import pandas_checks` in your code. That changes what happens when you use regular Pandas dataframes:
    ```
    import pandas as pd
    import pandas_checks
    ```

Now new methods are accessible to Pandas dataframes as ".check":

    ```
    (
        pd.DataFrame(my_data)
        .assign(new_column=4)
        .check.value_counts()       # <-- New methods available
        .assign(another_column=15)
    )
    ```

All public .check methods display the result but then return the unchanged DataFrame, so a method chain continues unbroken.
"""

from datetime import datetime, timedelta
from typing import Any, Callable, List, Type, Union

import matplotlib.pyplot as plt
import pandas as pd
from pandas.core.groupby.groupby import DataError

from .display import (
    _display_line,
    _display_plot,
    _display_plot_title,
    _display_table_title,
)
from .options import (
    disable_checks,
    enable_checks,
    get_mode,
    reset_format,
    set_format,
    set_mode,
)
from .run_checks import _apply_modifications, _check_data
from .timer import print_time_elapsed
from .utils import _has_nulls, _is_type, _lambda_to_string


@pd.api.extensions.register_dataframe_accessor("check")
class DataFrameChecks:
    def __init__(self, pandas_obj: Union[pd.DataFrame, pd.Series]) -> None:
        self._obj = pandas_obj

    def assert_all_nulls(
        self,
        fail_message: str = " ㄨ Assert all nulls failed ",
        pass_message: str = " ✔️ Assert all nulls passed ",
        subset: Union[str, List, None] = None,
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = DataError,
        verbose: bool = False,
    ) -> pd.DataFrame:
        """Tests whether Dataframe or subset of columns has all nulls. Optionally raises an exception. Does not modify the DataFrame itself.

        Example:
            ```python
                (
                    iris
                    .check.assert_all_nulls(subset=["sepal_length"])
                )

                # Will raise an exception "ㄨ Assert all nulls failed"

            ```
            See docs for `.check.assert_data()` for examples of how to customize assertions.

        Args:
            fail_message: Message to display if the condition fails.
            pass_message: Message to display if the condition passes.
            subset: Optional, which column or columns to check the condition against.
            raise_exception: Whether to raise an exception if the condition fails.
            exception_to_raise: The exception to raise if the condition fails and raise_exception is True.
            verbose: Whether to display the pass message if the condition passes.

        Returns:
            The original DataFrame, unchanged.
        """

        self._obj.check.assert_data(
            condition=lambda df: df.isna().all().all(),
            fail_message=fail_message,
            pass_message=pass_message,
            subset=subset,
            raise_exception=raise_exception,
            exception_to_raise=exception_to_raise,
            message_shows_condition=False,
            verbose=verbose,
        )
        return self._obj

    def assert_data(
        self,
        condition: Callable,
        fail_message: str = " ㄨ Assertion failed ",
        pass_message: str = " ✔️ Assertion passed ",
        subset: Union[str, List, None] = None,
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = DataError,
        message_shows_condition: bool = True,
        verbose: bool = False,
    ) -> pd.DataFrame:
        """Tests whether Dataframe meets condition. Optionally raises an exception. Does not modify the DataFrame itself.

        Example:
            ```python
                # Validate that the Dataframe has at least 1 row

                (
                    iris
                    .check.assert_data(lambda df: df.shape[0]>0)

                    # Or customize the message displayed when assert fails
                    .check.assert_data(lambda df: df.shape[0]>0, "Assertion failed, DataFrame has no rows!")

                    # Or show a warning instead of raising an exception
                    .check.assert_data(lambda df: s.shape[0]>0, "FYI DataFrame has no rows", raise_exception=False)

                    # Or show a message if it passes, and raise a specific exception (ValueError) if it fails.
                    .check.assert_data(
                        lambda df: s.shape[0]>0,
                        fail_message="FYI DataFrame has 0 rows",
                        pass_message="DataFrame has at least 1 row!",
                        exception_to_raise=ValueError,
                        verbose=True # To show pass_message when assertion passes
                        )
                )
            ```

        Args:
            condition: Assertion criteria in the form of a lambda function, such as `lambda df: df.shape[0]>10`.
            fail_message: Message to display if the condition fails.
            pass_message: Message to display if the condition passes.
            subset: Optional, which column or columns to check the condition against. Applied after fn. Subsetting can also be done within the `condition`, such as `lambda df: df['column_name'].sum()>10`
            raise_exception: Whether to raise an exception if the condition fails.
            exception_to_raise: The exception to raise if the condition fails and raise_exception is True.
            message_shows_condition: Whether the fail/pass message should also print the assertion criteria
            verbose: Whether to display the pass message if the condition passes.

        Returns:
            The original DataFrame, unchanged.
        """
        if not get_mode()["enable_asserts"]:
            return self._obj
        if not callable(condition):
            raise TypeError(
                f"Expected condition to be a lambda function (callable type) but received type {type(condition)}"
            )
        data = self._obj[subset] if subset else self._obj
        result = condition(data)
        condition_str = _lambda_to_string(condition)

        # Fail
        if not result:
            if raise_exception:
                raise exception_to_raise(
                    f"{fail_message}{' :' + condition_str if condition_str and message_shows_condition else ''}"
                )
            else:
                if message_shows_condition:
                    _display_line(
                        lead_in=fail_message,
                        line=condition_str,
                        colors={
                            "lead_in_text_color": pd.get_option(
                                "pdchecks.fail_message_fg_color"
                            ),
                            "lead_in_background_color": pd.get_option(
                                "pdchecks.fail_message_bg_color"
                            ),
                        },
                    )
                else:
                    _display_line(
                        line=fail_message,
                        colors={
                            "text_color": pd.get_option(
                                "pdchecks.fail_message_fg_color"
                            ),
                            "text_background_color": pd.get_option(
                                "pdchecks.fail_message_bg_color"
                            ),
                        },
                    )

        # Pass
        if result and verbose:
            if message_shows_condition:
                _display_line(
                    lead_in=pass_message,
                    line=condition_str,
                    colors={
                        "lead_in_text_color": pd.get_option(
                            "pdchecks.pass_message_fg_color"
                        ),
                        "lead_in_background_color": pd.get_option(
                            "pdchecks.pass_message_bg_color"
                        ),
                    },
                )
            else:
                _display_line(
                    line=pass_message,
                    colors={
                        "text_color": pd.get_option("pdchecks.pass_message_fg_color"),
                        "text_background_color": pd.get_option(
                            "pdchecks.pass_message_bg_color"
                        ),
                    },
                )

        return self._obj

    def assert_datetime(
        self,
        fail_message: Union[str, None] = None,
        pass_message: str = " ✔️ Assert datetime passed ",
        subset: Union[str, List, None] = None,
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = TypeError,
        verbose: bool = False,
    ) -> pd.DataFrame:
        """Tests whether Dataframe or subset of columns is datetime or timestamp. Optionally raises an exception. Does not modify the DataFrame itself.

        Example:
            ```python
                (
                    df
                    .check.assert_datetime(subset="datetime_col")
                )
            ```

            See docs for `.check.assert_data()` for examples of how to customize assertions.

        Args:
            subset: Optional, which column or columns to check the condition against.
            fail_message: Message to display if the condition fails. If None, will report expected vs observed type.
            pass_message: Message to display if the condition passes.
            raise_exception: Whether to raise an exception if the condition fails.
            exception_to_raise: The exception to raise if the condition fails and raise_exception is True.
            verbose: Whether to display the pass message if the condition passes.

        Returns:
            The original DataFrame, unchanged.
        """

        self._obj.check.assert_type(
            dtype=datetime,
            fail_message=fail_message,
            pass_message=pass_message,
            subset=subset,
            raise_exception=raise_exception,
            exception_to_raise=exception_to_raise,
            verbose=verbose,
        )
        return self._obj

    def assert_float(
        self,
        fail_message: Union[str, None] = None,
        pass_message: str = " ✔️ Assert float passed ",
        subset: Union[str, List, None] = None,
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = TypeError,
        verbose: bool = False,
    ) -> pd.DataFrame:
        """Tests whether Dataframe or subset of columns is floats. Optionally raises an exception. Does not modify the DataFrame itself.

        Example:
            ```python
                (
                    df
                    .check.assert_float(subset="float_col")
                )

            ```

            See docs for `.check.assert_data()` for examples of how to customize assertions.

        Args:
            fail_message: Message to display if the condition fails.
            pass_message: Message to display if the condition passes.
            subset: Optional, which column or columns to check the condition against.
            raise_exception: Whether to raise an exception if the condition fails.
            exception_to_raise: The exception to raise if the condition fails and raise_exception is True.
            verbose: Whether to display the pass message if the condition passes.

        Returns:
            The original DataFrame, unchanged.
        """

        self._obj.check.assert_type(
            dtype=float,
            fail_message=fail_message,
            pass_message=pass_message,
            subset=subset,
            raise_exception=raise_exception,
            exception_to_raise=exception_to_raise,
            verbose=verbose,
        )
        return self._obj

    def assert_greater_than(
        self,
        min: Any,
        fail_message: str = " ㄨ Assert minimum failed ",
        pass_message: str = " ✔️ Assert minimum passed ",
        or_equal_to: bool = False,
        subset: Union[str, List, None] = None,
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = DataError,
        verbose: bool = False,
    ) -> pd.DataFrame:
        """Tests whether all values in a Dataframe or subset of columns is > or >= a minimum threshold. Optionally raises an exception. Does not modify the DataFrame itself.


        Example:
            ```python
                (
                    iris
                    # Validate that sepal_length is always greater than 0.1
                    .check.assert_greater_than(0.1, subset="sepal_length")

                    # Validate that two columns are each always greater than or equal to 0.1
                    .check.assert_greater_than(0.1, subset=["sepal_length", "petal_length"], or_equal_to=True)
                )

            ```

            See docs for `.check.assert_data()` for examples of how to customize assertions.

        Args:
            min: the minimum value to compare DataFrame to. Accepts any type that can be used in >, such as int, float, str, datetime
            fail_message: Message to display if the condition fails.
            pass_message: Message to display if the condition passes.
            or_equal_to: whether to test for >= min (True) or > min (False)
            subset: Optional, which column or columns to check the condition against.
            raise_exception: Whether to raise an exception if the condition fails.
            exception_to_raise: The exception to raise if the condition fails and raise_exception is True.
            verbose: Whether to display the pass message if the condition passes.

        Returns:
            The original DataFrame, unchanged.
        """
        if or_equal_to:
            min_fn = lambda df: (df >= min).all().all()
        else:
            min_fn = lambda df: (df > min).all().all()

        self._obj.check.assert_data(
            condition=min_fn,
            fail_message=fail_message,
            pass_message=pass_message,
            subset=subset,
            raise_exception=raise_exception,
            exception_to_raise=exception_to_raise,
            message_shows_condition=False,
            verbose=verbose,
        )
        return self._obj

    def assert_int(
        self,
        fail_message: Union[str, None] = None,
        pass_message: str = " ✔️ Assert integeer passed ",
        subset: Union[str, List, None] = None,
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = TypeError,
        verbose: bool = False,
    ) -> pd.DataFrame:
        """Tests whether Dataframe or subset of columns is integers. Optionally raises an exception. Does not modify the DataFrame itself.

        Example:
            ```python
                (
                    df
                    .check.assert_int(subset="int_col")
                )
            ```

            See docs for `.check.assert_data()` for examples of how to customize assertions.

        Args:
            fail_message: Message to display if the condition fails.
            pass_message: Message to display if the condition passes.
            subset: Optional, which column or columns to check the condition against.
            raise_exception: Whether to raise an exception if the condition fails.
            exception_to_raise: The exception to raise if the condition fails and raise_exception is True.
            verbose: Whether to display the pass message if the condition passes.

        Returns:
            The original DataFrame, unchanged.
        """

        self._obj.check.assert_type(
            dtype=int,
            fail_message=fail_message,
            pass_message=pass_message,
            subset=subset,
            raise_exception=raise_exception,
            exception_to_raise=exception_to_raise,
            verbose=verbose,
        )
        return self._obj

    def assert_less_than(
        self,
        max: Any,
        fail_message: str = " ㄨ Assert maximum failed ",
        pass_message: str = " ✔️ Assert maximum passed ",
        or_equal_to: bool = False,
        subset: Union[str, List, None] = None,
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = DataError,
        verbose: bool = False,
    ) -> pd.DataFrame:
        """Tests whether all values in a Dataframe or subset of columns is < or <= a maximum threshold. Optionally raises an exception. Does not modify the DataFrame itself.

        Example:
            ```python
                (
                    iris

                    # Validate that sepal_length is always < 1000
                    .check.assert_less_than(1000, subset="sepal_length")

                    # Validate that two columns are each always less than or equal too 100
                    .check.assert_less_than(1000, subset=["sepal_length", "petal_length"], or_equal_to=True)
                )
            ```

            See docs for `.check.assert_data()` for examples of how to customize assertions.

        Args:
            max: the max value to compare DataFrame to. Accepts any type that can be used in <, such as int, float, str, datetime
            or_equal_to: whether to test for <= max (True) or < max (False)
            fail_message: Message to display if the condition fails.
            pass_message: Message to display if the condition passes.
            subset: Optional, which column or columns to check the condition against.
            raise_exception: Whether to raise an exception if the condition fails.
            exception_to_raise: The exception to raise if the condition fails and raise_exception is True.
            verbose: Whether to display the pass message if the condition passes.

        Returns:
            The original DataFrame, unchanged.
        """
        if or_equal_to:
            max_fn = lambda df: (df <= max).all().all()
        else:
            max_fn = lambda df: (df < max).all().all()

        self._obj.check.assert_data(
            condition=max_fn,
            fail_message=fail_message,
            pass_message=pass_message,
            subset=subset,
            raise_exception=raise_exception,
            exception_to_raise=exception_to_raise,
            message_shows_condition=False,
            verbose=verbose,
        )
        return self._obj

    def assert_negative(
        self,
        fail_message: str = " ㄨ Assert negative failed ",
        pass_message: str = " ✔️ Assert negative passed ",
        subset: Union[str, List, None] = None,
        assert_no_nulls: bool = True,
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = DataError,
        verbose: bool = False,
    ) -> pd.DataFrame:
        """Tests whether Dataframe or subset of columns has all negative values. Optionally raises an exception. Does not modify the DataFrame itself.

        Example:
            ```python
                (
                    df
                    .check.assert_negative(subset="column_name")
                )
            ```
            See docs for `.check.assert_data()` for examples of how to customize assertions.

        Args:
            fail_message: Message to display if the condition fails.
            pass_message: Message to display if the condition passes.
            subset: Optional, which column or columns to check the condition against.`
            assert_no_nulls: Whether to also enforce that data has no nulls.
            raise_exception: Whether to raise an exception if the condition fails.
            exception_to_raise: The exception to raise if the condition fails and raise_exception is True.
            verbose: Whether to display the pass message if the condition passes.

        Returns:
            The original DataFrame, unchanged.
        """

        if assert_no_nulls:
            if _has_nulls(
                data=self._obj[subset] if subset else self._obj,
                fail_message=fail_message,
                raise_exception=raise_exception,
                exception_to_raise=exception_to_raise,
            ):
                # _has_nulls() will raise exception or print failure
                return self._obj

        self._obj.dropna().check.assert_data(
            condition=lambda df: (df < 0).all().all(),
            fail_message=fail_message,
            pass_message=pass_message,
            subset=subset,
            raise_exception=raise_exception,
            exception_to_raise=exception_to_raise,
            message_shows_condition=False,
            verbose=verbose,
        )
        return self._obj

    def assert_no_nulls(
        self,
        fail_message: str = " ㄨ Assert no nulls failed ",
        pass_message: str = " ✔️ Assert no nulls passed ",
        subset: Union[str, List, None] = None,
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = DataError,
        verbose: bool = False,
    ) -> pd.DataFrame:
        """Tests whether Dataframe or subset of columns has no nulls. Optionally raises an exception. Does not modify the DataFrame itself.

        Example:
            ```python
                (
                    iris
                    .check.assert_no_nulls(subset=["sepal_length"])
                )
            ```

            See docs for `.check.assert_data()` for examples of how to customize assertions.

        Args:
            fail_message: Message to display if the condition fails.
            pass_message: Message to display if the condition passes.
            subset: Optional, which column or columns to check the condition against.
            raise_exception: Whether to raise an exception if the condition fails.
            exception_to_raise: The exception to raise if the condition fails and raise_exception is True.
            verbose: Whether to display the pass message if the condition passes.

        Returns:
            The original DataFrame, unchanged.
        """

        self._obj.check.assert_data(
            condition=lambda df: df.isna().any().any() == False,
            fail_message=fail_message,
            pass_message=pass_message,
            subset=subset,
            raise_exception=raise_exception,
            exception_to_raise=exception_to_raise,
            message_shows_condition=False,
            verbose=verbose,
        )
        return self._obj

    def assert_nrows(
        self,
        nrows: int,
        fail_message: str = " ㄨ Assert nrows failed ",
        pass_message: str = " ✔️ Assert nrows passed ",
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = DataError,
        verbose: bool = False,
    ) -> pd.DataFrame:
        """Tests whether Dataframe has a given number of rows. Optionally raises an exception. Does not modify the DataFrame itself.

        Example:
            ```python
                (
                    iris
                    .check.assert_nrows(20)
                )
            ```

            See docs for `.check.assert_data()` for examples of how to customize assertions.

        Args:
            nrows: The expected number of rows
            fail_message: Message to display if the condition fails.
            pass_message: Message to display if the condition passes.
            raise_exception: Whether to raise an exception if the condition fails.
            exception_to_raise: The exception to raise if the condition fails and raise_exception is True.
            verbose: Whether to display the pass message if the condition passes.

        Returns:
            The original DataFrame, unchanged.
        """

        self._obj.check.assert_data(
            condition=lambda df: df.shape[0] == nrows,
            fail_message=fail_message,
            pass_message=pass_message,
            raise_exception=raise_exception,
            exception_to_raise=exception_to_raise,
            message_shows_condition=False,
            verbose=verbose,
        )
        return self._obj

    def assert_positive(
        self,
        fail_message: str = " ㄨ Assert positive failed ",
        pass_message: str = " ✔️ Assert positive passed ",
        subset: Union[str, List, None] = None,
        assert_no_nulls: bool = True,
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = DataError,
        verbose: bool = False,
    ) -> pd.DataFrame:
        """Tests whether Dataframe or subset of columns has all positive values. Optionally raises an exception. Does not modify the DataFrame itself.

        Example:
            ```python
                (
                    iris
                    .check.assert_positive(subset=["sepal_length"])
                )
            ```

            See docs for `.check.assert_data()` for examples of how to customize assertions.

        Args:
            fail_message: Message to display if the condition fails.
            pass_message: Message to display if the condition passes.
            subset: Optional, which column or columns to check the condition against.
            assert_no_nulls: Whether to also enforce that data has no nulls.
            raise_exception: Whether to raise an exception if the condition fails.
            exception_to_raise: The exception to raise if the condition fails and raise_exception is True.
            verbose: Whether to display the pass message if the condition passes.

        Returns:
            The original DataFrame, unchanged.
        """
        if assert_no_nulls:
            if _has_nulls(
                data=self._obj[subset] if subset else self._obj,
                fail_message=fail_message,
                raise_exception=raise_exception,
                exception_to_raise=exception_to_raise,
            ):
                # _has_nulls() will raise exception or print failure
                return self._obj

        self._obj.dropna().check.assert_data(
            condition=lambda df: (df > 0).all().all(),
            fail_message=fail_message,
            pass_message=pass_message,
            subset=subset,
            raise_exception=raise_exception,
            exception_to_raise=exception_to_raise,
            message_shows_condition=False,
            verbose=verbose,
        )
        return self._obj

    def assert_same_nrows(
        self,
        other: Union[pd.DataFrame, pd.Series],
        fail_message: str = " ㄨ Assert same_nrows failed ",
        pass_message: str = " ✔️ Assert same_nrows passed ",
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = DataError,
        verbose: bool = False,
    ) -> pd.DataFrame:
        """Tests whether Dataframe has the same number of rows as another DataFrame/Series has.

        Optionally raises an exception. Does not modify the DataFrame itself.

        Example:
            ```python
                # Validate that an expected one-to-one join didn't add rows due to duplicate keys in the right table.
                (
                    transactions_df
                    .merge(how="left", right=products_df, on="product_id")
                    .check.assert_same_nrows(transactions_df, "Left join changed row count! Check for duplicate `product_id` keys in product_df.")
                )
            ```

            See docs for `.check.assert_data()` for examples of how to customize assertions.

        Args:
            other: The DataFrame or Series that we expect to have the same # of rows as
            fail_message: Message to display if the condition fails.
            pass_message: Message to display if the condition passes.
            raise_exception: Whether to raise an exception if the condition fails.
            exception_to_raise: The exception to raise if the condition fails and raise_exception is True.
            verbose: Whether to display the pass message if the condition passes.

        Returns:
            The original DataFrame, unchanged.
        """

        self._obj.check.assert_data(
            condition=lambda df: df.shape[0] == other.shape[0],
            fail_message=fail_message,
            pass_message=pass_message,
            raise_exception=raise_exception,
            exception_to_raise=exception_to_raise,
            message_shows_condition=False,
            verbose=verbose,
        )
        return self._obj

    def assert_str(
        self,
        fail_message: Union[str, None] = None,
        pass_message: str = " ✔️ Assert string passed ",
        subset: Union[str, List, None] = None,
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = TypeError,
        verbose: bool = False,
    ) -> pd.DataFrame:
        """Tests whether Dataframe or subset of columns is strings. Optionally raises an exception. Does not modify the DataFrame itself.

        Example:
            ```python
                (
                    iris
                    .check.assert_str(subset=["species", "another_string_column"])
                )
            ```

            See docs for `.check.assert_data()` for examples of how to customize assertions.

        Args:
            fail_message: Message to display if the condition fails. If None, will report expected vs observed type.
            pass_message: Message to display if the condition passes.
            subset: Optional, which column or columns to check the condition against.
            raise_exception: Whether to raise an exception if the condition fails.
            exception_to_raise: The exception to raise if the condition fails and raise_exception is True.
            verbose: Whether to display the pass message if the condition passes.

        Returns:
            The original DataFrame, unchanged.
        """

        self._obj.check.assert_type(
            dtype=str,
            fail_message=fail_message,
            pass_message=pass_message,
            subset=subset,
            raise_exception=raise_exception,
            exception_to_raise=exception_to_raise,
            verbose=verbose,
        )
        return self._obj

    def assert_timedelta(
        self,
        fail_message: Union[str, None] = None,
        pass_message: str = " ✔️ Assert timedelta passed ",
        subset: Union[str, List, None] = None,
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = TypeError,
        verbose: bool = False,
    ) -> pd.DataFrame:
        """Tests whether Dataframe or subset of columns is of type timedelta. Optionally raises an exception. Does not modify the DataFrame itself.

        Example:
            ```python
                (
                    df
                    .check.assert_timedelta(subset=["timedelta_col"])
                )
            ```

            See docs for `.check.assert_data()` for examples of how to customize assertions.

        Args:
            fail_message: Message to display if the condition fails. If None, will report expected vs observed type.
            pass_message: Message to display if the condition passes.
            subset: Optional, which column or columns to check the condition against.
            raise_exception: Whether to raise an exception if the condition fails.
            exception_to_raise: The exception to raise if the condition fails and raise_exception is True.
            verbose: Whether to display the pass message if the condition passes.

        Returns:
            The original DataFrame, unchanged.
        """

        self._obj.check.assert_type(
            dtype=timedelta,
            fail_message=fail_message,
            pass_message=pass_message,
            subset=subset,
            raise_exception=raise_exception,
            exception_to_raise=exception_to_raise,
            verbose=verbose,
        )
        return self._obj

    def assert_type(
        self,
        dtype: Type[Any],
        fail_message: Union[str, None] = None,
        pass_message: str = " ✔️ Assert type passed ",
        subset: Union[str, List, None] = None,
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = TypeError,
        verbose: bool = False,
    ) -> pd.DataFrame:
        """Tests whether Dataframe or subset of columns meets type assumption. Optionally raises an exception. Does not modify the DataFrame itself.

        Example:
            ```python
                # Validate that a column of mixed types has overall type `object`
                (
                    iris
                    .check.assert_type(object, subset="column_with_mixed_types")
                )
            ```

            See docs for `.check.assert_data()` for examples of how to customize assertions.

        Args:
            dtype: The required variable type
            fail_message: Message to display if the condition fails. If None, will report expected vs observed type.
            pass_message: Message to display if the condition passes.
            subset: Optional, which column or columns to check the condition against.
            raise_exception: Whether to raise an exception if the condition fails.
            exception_to_raise: The exception to raise if the condition fails and raise_exception is True.
            verbose: Whether to display the pass message if the condition passes.

        Returns:
            The original DataFrame, unchanged.
        """

        if not subset:
            subset = self._obj.columns.tolist()
        elif isinstance(subset, str):
            subset = [subset]
        elif isinstance(
            subset, tuple
        ):  # Single multiindex, like in brain_networks.csv test case
            subset = [subset]

        found_dtypes = ", ".join([t.name for t in self._obj[subset].dtypes.values])
        if not fail_message:
            dtype_clean = (
                str(dtype).replace("<class", "").replace(">", "").replace("'", "")
            )  # <class > types will get blanked out in our HTML display
            fail_message = (
                f" ㄨ Assert type failed: expected {dtype_clean}, got {found_dtypes}"
            )
        self._obj.check.assert_data(
            condition=lambda df: _is_type(df, dtype),
            fail_message=fail_message,
            pass_message=pass_message,
            subset=subset,
            raise_exception=raise_exception,
            exception_to_raise=exception_to_raise,
            message_shows_condition=False,
            verbose=verbose,
        )
        return self._obj

    def assert_unique(
        self,
        fail_message: str = " ㄨ Assert unique failed ",
        pass_message: str = " ✔️ Assert unique passed ",
        subset: Union[str, List, None] = None,
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = DataError,
        verbose: bool = False,
    ) -> pd.DataFrame:
        """Validates that a subset of columns have no duplicate values, or validates that a DataFrame has no duplicate rows. Optionally raises an exception. Does not modify the DataFrame itself.

        Example:
            ```python
                (
                    df
                    # Validate that a column has no duplicate values
                    .check.assert_unique(subset="id_column")

                    # Validate that a DataFrame has no duplicate rows
                    .check.assert_unique()
                )
            ```

            See docs for `.check.assert_data()` for examples of how to customize assertions.

        Args:
            fail_message: Message to display if the condition fails.
            pass_message: Message to display if the condition passes.
            subset: Optional, which column or columns to check the condition against.
            raise_exception: Whether to raise an exception if the condition fails.
            exception_to_raise: The exception to raise if the condition fails and raise_exception is True.
            verbose: Whether to display the pass message if the condition passes.

        Returns:
            The original DataFrame, unchanged.
        """

        self._obj.check.assert_data(
            condition=lambda df: df.duplicated().sum() == 0,
            fail_message=fail_message,
            pass_message=pass_message,
            subset=subset,
            raise_exception=raise_exception,
            exception_to_raise=exception_to_raise,
            message_shows_condition=False,
            verbose=verbose,
        )
        return self._obj

    def columns(
        self,
        fn: Callable = lambda df: df,
        subset: Union[str, List, None] = None,
        check_name: Union[str, None] = "🏛️ Columns",
    ) -> pd.DataFrame:
        """Prints the column names of a DataFrame, without modifying the DataFrame itself.

        Example:
            ```python
                (
                    df
                    .check.columns()
                )
            ```

        Args:
            fn: An optional lambda function to apply to the DataFrame before printing columns. Example: `lambda df: df.shape[0]>10`. Applied before subset.
            subset: An optional list of column names or a string to select a subset of columns before printing their names. Applied after fn.
            check_name: An optional name for the check to preface the result with.

        Returns:
            The original DataFrame, unchanged.
        """
        _check_data(
            self._obj,
            check_fn=lambda df: df.columns.tolist(),
            modify_fn=fn,
            subset=subset,
            check_name=check_name,
        )
        return self._obj

    def describe(
        self,
        fn: Callable = lambda df: df,
        subset: Union[str, List, None] = None,
        check_name: Union[str, None] = "📏 Distributions",
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Displays descriptive statistics about a DataFrame without modifying the DataFrame itself.

        See Pandas docs for [describe()](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.describe.html) for additional usage information, including more configuration options you can pass to this Pandas Checks method.

        Example:
            ```python
                (
                    df
                    .check.describe()
                )
            ```

        Args:
            fn: An optional lambda function to apply to the DataFrame before running Pandas describe(). Example: `lambda df: df.shape[0]>10`. Applied before subset.
            subset: An optional list of column names or a string to select a subset of columns before running Pandas describe(). Applied after fn.
            check_name: An optional name for the check to preface the result with.
            **kwargs: Optional, additional arguments that are accepted by Pandas describe() method.

        Returns:
            The original DataFrame, unchanged.
        """
        _check_data(
            self._obj,
            check_fn=lambda df: df.describe(**kwargs),
            modify_fn=fn,
            subset=subset,
            check_name=check_name,
        )
        return self._obj

    def disable_checks(self, enable_asserts: bool = True) -> pd.DataFrame:
        """Turns off Pandas Checks globally, such as in production mode. Calls to .check functions will not be run. Does not modify the DataFrame itself.

        Example:
            ```python
                (
                    iris
                    .check.disable_checks()
                    .check.assert_data(lambda df: df.shape[0]>10) #  This check will NOT be run
                    .check.enable_checks() # Subsequent calls to .check will be run
                )
            ```

        Args
            enable_assert: Optionally, whether to also enable or disable assert statements

        Returns:
            The original DataFrame, unchanged.
        """
        disable_checks(enable_asserts)
        return self._obj

    def dtypes(
        self,
        fn: Callable = lambda df: df,
        subset: Union[str, List, None] = None,
        check_name: Union[str, None] = "🗂️ Data types",
    ) -> pd.DataFrame:
        """Displays the data types of a DataFrame's columns without modifying the DataFrame itself.

        Example:
            ```python
                (
                    iris
                    .check.dtypes()
                )
            ```

        Args:
            fn: An optional lambda function to apply to the DataFrame before running Pandas dtypes. Example: `lambda df: df.shape[0]>10`. Applied before subset.
            subset: An optional list of column names or a string to select a subset of columns before running Pandas .dtypes. Applied after fn.
            check_name: An optional name for the check to preface the result with.

        Returns:
            The original DataFrame, unchanged.
        """
        _check_data(
            self._obj,
            check_fn=lambda df: df.dtypes,
            modify_fn=fn,
            subset=subset,
            check_name=check_name,
        )
        return self._obj

    def enable_checks(self, enable_asserts: bool = True) -> pd.DataFrame:
        """Globally enables Pandas Checks. Subequent calls to .check methods will be run. Does not modify the DataFrame itself.

        Example:
            ```python
                (
                    iris
                    ["sepal_length"]
                    .check.disable_checks()
                    .check.assert_data(lambda s: s.shape[0]>10) #  This check will NOT be run
                    .check.enable_checks() # Subsequent calls to .check will be run
                )
            ```

        Args:
            enable_asserts: Optionally, whether to globally enable or disable calls to .check.assert_data().

        Returns:
            The original DataFrame, unchanged.
        """
        enable_checks(enable_asserts)
        return self._obj

    def function(
        self,
        fn: Callable = lambda df: df,
        subset: Union[str, List, None] = None,
        check_name: Union[str, None] = None,
    ) -> pd.DataFrame:
        """Applies an arbitrary function on a DataFrame and shows the result, without modifying the DataFrame itself.

        Example:
            ```python
                (
                    iris
                    .check.function(fn=lambda df: df.shape[0]>10, check_name='Has at least 10 rows?')
                )
                # Will return either 'True' or 'False'
            ```

        Args:
            fn: A lambda function to apply to the DataFrame. Example: `lambda df: df.shape[0]>10`. Applied before subset.
            subset: An optional list of column names or a string to select a subset of columns before running Pandas describe(). Applied after fn.
            check_name: An optional name for the check to preface the result with.

        Returns:
            The original DataFrame, unchanged.
        """
        _check_data(self._obj, modify_fn=fn, subset=subset, check_name=check_name)
        return self._obj

    def get_mode(
        self, check_name: Union[str, None] = "🐼🩺 Pandas Checks mode"
    ) -> pd.DataFrame:
        """Displays the current values of Pandas Checks global options enable_checks and enable_asserts. Does not modify the DataFrame itself.

        Example:
            ```python
                (
                    iris
                    .check.get_mode()
                )

                # The check will print:
                # "🐼🩺 Pandas Checks mode: {'enable_checks': True, 'enable_asserts': True}"
            ```

        Args:
            check_name: An optional name for the check. Will be used as a preface the printed result.

        Returns:
            The original DataFrame, unchanged.
        """
        _display_line(lead_in=check_name, line=str(get_mode()))
        return self._obj

    def head(
        self,
        n: int = 5,
        fn: Callable = lambda df: df,
        subset: Union[str, List, None] = None,
        check_name: Union[str, None] = None,
    ) -> pd.DataFrame:
        """Displays the first n rows of a DataFrame, without modifying the DataFrame itself.

        See Pandas docs for [head()](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.head.html) for additional usage information.

        Example:
            ```python
                (
                    iris
                    .check.head(10)
                )
            ```

        Args:
            n: The number of rows to display.
            fn: An optional lambda function to apply to the DataFrame before running Pandas head(). Example: `lambda df: df.shape[0]>10`. Applied before subset.
            subset: An optional list of column names or a string to select a subset of columns before running Pandas head(). Applied after fn.
            check_name: An optional name for the check, to be printed as preface to the result.

        Returns:
            The original DataFrame, unchanged.
        """
        _check_data(
            self._obj,
            check_fn=lambda df: df.head(n),
            modify_fn=fn,
            subset=subset,
            check_name=check_name if check_name else f"⬆️ First {n} rows",
        )
        return self._obj

    def hist(
        self,
        fn: Callable = lambda df: df,
        subset: Union[str, List, None] = [],
        check_name: Union[str, None] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Displays a histogram for the DataFrame, without modifying the DataFrame itself.

        See Pandas docs for [hist()](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.hist.html) for additional usage information, including more configuration options you can pass to this Pandas Checks method.

        Example:
            ```python
                (
                    iris
                    .check.hist(subset=["sepal_length", "sepal_width"])
                )
            ```

        Args:
            fn: An optional lambda function to apply to the DataFrame before running Pandas hist(). Example: `lambda df: df.shape[0]>10`. Applied before subset.
            subset: An optional list of column names or a string to select a subset of columns before running Pandas hist(). Applied after fn.
            check_name: An optional name for the check, to be printed as preface to the result.
            **kwargs: Optional, additional arguments that are accepted by Pandas hist() method.

        Returns:
            The original DataFrame, unchanged.

        Note:
            If more than one column is passed, displays a grid of histograms.

            Only renders in interactive mode (IPython/Jupyter), not in terminal.
        """
        if (
            get_mode()["enable_checks"] and not pd.core.config_init.is_terminal()
        ):  # Only display if in IPython/Jupyter, or we'd just print the title
            _display_plot_title(
                check_name
                if check_name
                else "📏 Distribution"
                if subset and len(subset) == 1
                else "📏 Distributions"
            )
            _ = _apply_modifications(self._obj, fn, subset).hist(**kwargs)
            _display_plot()
        return self._obj

    def info(
        self,
        fn: Callable = lambda df: df,
        subset: Union[str, List, None] = None,
        check_name: Union[str, None] = "ℹ️ Info",
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Displays summary information about a DataFrame, without modifying the DataFrame itself.

        See Pandas docs for [info()](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.info.html) for additional usage information, including more configuration options you can pass to this Pandas Checks method.

        Example:
            ```python
                (
                    iris
                    .check.info()
                )
            ```

        Args:
            fn: An optional lambda function to apply to the DataFrame before running Pandas info(). Example: `lambda df: df.shape[0]>10`. Applied before subset.
            subset: An optional list of column names or a string to select a subset of columns before running Pandas info(). Applied after fn.
            check_name: An optional name for the check, to be printed as preface to the result.
            **kwargs: Optional, additional arguments that are accepted by Pandas info() method.

        Returns:
            The original DataFrame, unchanged.
        """
        if get_mode()["enable_checks"]:
            if check_name:
                _display_table_title(check_name)
            (_apply_modifications(self._obj, fn, subset).info(**kwargs))
        return self._obj

    def memory_usage(
        self,
        fn: Callable = lambda df: df,
        subset: Union[str, List, None] = None,
        check_name: Union[str, None] = "💾 Memory usage",
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Displays the memory footprint of a DataFrame, without modifying the DataFrame itself.

        See Pandas docs for [memory_usage()](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.memory_usage.html) for additional usage information, including more configuration options you can pass to this Pandas Checks method.

        Example:
            ```python
                (
                    iris
                    .check.memory_usage()
                )
            ```

        Args:
            fn: An optional lambda function to apply to the DataFrame before running Pandas memory_usage(). Example: `lambda df: df.shape[0]>10`. Applied before subset.
            subset: An optional list of column names or a string to select a subset of columns before running Pandas memory_usage(). Applied after fn.
            check_name: An optional name for the check, to be printed as preface to the result.
            **kwargs: Optional, additional arguments that are accepted by Pandas info() method.

        Returns:
            The original DataFrame, unchanged.

        Note:
            Include argument `deep=True` to get further memory usage of object dtypes in the DataFrame. See Pandas docs for [memory_usage()](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.memory_usage.html) for more info.
        """
        _check_data(
            self._obj,
            check_fn=lambda df: df.memory_usage(**kwargs),
            modify_fn=fn,
            subset=subset,
            check_name=check_name,
        )
        return self._obj

    def ncols(
        self,
        fn: Callable = lambda df: df,
        subset: Union[str, List, None] = None,
        check_name: Union[str, None] = "🏛️ Columns",
    ) -> pd.DataFrame:
        """Displays the number of columns in a DataFrame, without modifying the DataFrame itself.

        Example:
            ```python
                (
                    iris
                    .check.ncols()
                )
            ```

        Args:
            fn: An optional lambda function to apply to the DataFrame before counting the number of columns. Example: `lambda df: df.shape[0]>10`. Applied before subset.
            subset: An optional list of column names or a string to select a subset of columns before counting the number of columns. Applied after fn.
            check_name: An optional name for the check, to be printed as preface to the result.

        Returns:
            The original DataFrame, unchanged.
        """
        _check_data(
            self._obj,
            check_fn=lambda df: df.shape[1],
            modify_fn=fn,
            subset=subset,
            check_name=check_name,
        )
        return self._obj

    def ndups(
        self,
        fn: Callable = lambda df: df,
        subset: Union[str, List, None] = None,
        check_name: Union[str, None] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Displays the number of duplicated rows in a DataFrame, without modifying the DataFrame itself.

        See Pandas docs for [duplicated()](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.duplicated.html) for additional usage information, including more configuration options you can pass to this Pandas Checks method.

        Example:
            ```python
                # Count the number of rows with duplicate pairs of values across two columns:
                (
                    iris
                    .check.ndups(subset=["sepal_length", "sepal_width"])
                )
            ```

        Args:
            fn: An optional lambda function to apply to the DataFrame before counting the number of duplicates. Example: `lambda df: df.shape[0]>10`. Applied before subset.
            subset: An optional list of column names or a string to select a subset of columns before counting duplicate rows. Applied after fn.
            check_name: An optional name for the check, to be printed as preface to the result.
            **kwargs: Optional, additional arguments that are accepted by Pandas duplicated() method.

        Returns:
            The original DataFrame, unchanged.
        """
        _check_data(
            self._obj,
            check_fn=lambda df: df.duplicated(**kwargs).sum(),
            modify_fn=fn,
            subset=subset,
            check_name=check_name
            if check_name
            else f"👯‍♂️ Rows with duplication in {subset}"
            if subset
            else "👯‍♂️ Duplicated rows",
        )
        return self._obj

    def nnulls(
        self,
        fn: Callable = lambda df: df,
        subset: Union[str, List, None] = None,
        by_column: bool = True,
        check_name: Union[str, None] = "👻 Rows with NaNs",
    ) -> pd.DataFrame:
        """Displays the number of rows with null values in a DataFrame, without modifying the DataFrame itself.

        See Pandas docs for [isna()](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.isna.html) for additional usage information.

        Example:
            ```python
                # Count the number of rows that have any nulls, one count per column
                (
                    iris
                    .check.nnulls()
                )

                # Count the number of rows in the DataFrame that have a null in any column
                (
                    iris
                    .check.nnulls(by_column=False)
                )
            ```

        Args:
            fn: An optional lambda function to apply to the DataFrame before counting the number of rows with a null. Example: `lambda df: df.shape[0]>10`. Applied before subset.
            subset: An optional list of column names or a string to select a subset of columns before counting nulls.
            by_column: If True, count null values with each column separately. If False, count rows with a null value in any column. Applied after fn.
            check_name: An optional name for the check, to be printed as preface to the result.

        Returns:
            The original DataFrame, unchanged.
        """
        if not get_mode()["enable_checks"]:
            return self._obj
        data = _apply_modifications(self._obj, fn, subset)
        na_counts = (
            data.isna().any(axis=1).sum()
            if isinstance(data, pd.DataFrame) and not by_column
            else data.isna().sum()
            if not by_column
            else pd.Series(data.isna().sum())
        )
        if isinstance(
            na_counts, (pd.DataFrame, pd.Series)
        ):  # Report result as a pandas object
            _check_data(
                na_counts,
                check_name=f"👻 Rows with NaNs in {subset}"
                if subset and not check_name
                else check_name,
            )
        else:  # Report on one line
            _display_line(
                (f"👻 Rows with NaNs in {subset}: {na_counts} out of {data.shape[0]}")
                if subset and not check_name
                else f"{check_name}: {na_counts}"
            )
        return self._obj

    def nrows(
        self,
        fn: Callable = lambda df: df,
        subset: Union[str, List, None] = None,
        check_name: Union[str, None] = "☰ Rows",
    ) -> pd.DataFrame:
        """Displays the number of rows in a DataFrame, without modifying the DataFrame itself.

        Example:
            ```python
                (
                    iris
                    .check.nrows()
                )
            ```

        Args:
            fn: An optional lambda function to apply to the DataFrame before counting the number of rows. Example: `lambda df: df.shape[0]>10`. Applied before subset.
            subset: An optional list of column names or a string name of one column to limit which columns are considered when counting rows. Applied after fn.
            check_name: An optional name for the check, to be printed as preface to the result.

        Returns:
            The original DataFrame, unchanged.
        """
        _check_data(
            self._obj,
            check_fn=lambda df: df.shape[0],
            modify_fn=fn,
            subset=subset,
            check_name=check_name,
        )
        return self._obj

    def nunique(
        self,
        column: str,
        fn: Callable = lambda df: df,
        check_name: Union[str, None] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Displays the number of unique rows in a single column, without modifying the DataFrame itself.

        See Pandas docs for [nunique()](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.nunique.html) for additional usage information, including more configuration options you can pass to this Pandas Checks method.

        Example:
            ```python
                (
                    iris
                    .check.nunique(column="sepal_width")
                )
            ```

        Args:
            column: The name of a column to count uniques in. Applied after fn.
            fn: An optional lambda function to apply to the DataFrame before running Pandas nunique(). Example: `lambda df: df.shape[0]>10`. Applied before subset.
            check_name: An optional name for the check, to be printed as preface to the result.
            **kwargs: Optional, additional arguments that are accepted by Pandas nunique() method.

        Returns:
            The original DataFrame, unchanged.
        """

        if get_mode()["enable_checks"]:
            (
                _apply_modifications(
                    self._obj, fn=fn, subset=column
                ).check.nunique(  # Apply fn, then filter to `column`, pass to SeriesChecks.check.nunique()
                    fn=lambda df: df,  # Identity function
                    check_name=check_name,
                    **kwargs,
                )
            )
        return self._obj

    def plot(
        self,
        fn: Callable = lambda df: df,
        subset: Union[str, List, None] = None,
        check_name: Union[str, None] = "",
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Displays a plot of the DataFrame, without modifying the DataFrame itself.

        See Pandas docs for [plot()](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.html) for additional usage information, including more configuration options you can pass to this Pandas Checks method.

        Example:
            ```python
                (
                    iris
                    .check.plot(kind="scatter", x="sepal_width", y="sepal_length", title="Sepal width vs sepal length")
                )
            ```

        Args:
            fn: An optional lambda function to apply to the DataFrame before running Pandas plot(). Example: `lambda df: df.shape[0]>10`. Applied before subset.
            subset: An optional list of column names or a string name of one column to limit which columns are plotted. Applied after fn.
            check_name: An optional title for the plot.
            **kwargs: Optional, additional arguments that are accepted by Pandas plot() method.

        Returns:
            The original DataFrame, unchanged.

        Note:
            Plots are only displayed when code is run in IPython/Jupyter, not in terminal.

            If you pass a 'title' kwarg, it becomes the plot title, overriding check_name
        """

        # Only display plot if in IPython/Jupyter. Or we'd just print its title.
        if get_mode()["enable_checks"] and not pd.core.config_init.is_terminal():
            _display_plot_title(
                check_name if "title" not in kwargs else kwargs["title"]
            )
            _ = _apply_modifications(self._obj, fn, subset).plot(**kwargs)
            _display_plot()
        return self._obj

    def print(
        self,
        object: Any = None,
        fn: Callable = lambda df: df,
        subset: Union[str, List, None] = None,
        check_name: Union[str, None] = None,
        max_rows: int = 10,
    ) -> pd.DataFrame:
        """Displays text, another object, or (by default) the current DataFrame's head. Does not modify the DataFrame itself.

        Example:
            ```python
                # Print messages and milestones
                (
                    iris
                    .check.print("Starting data cleaning..."")
                    ...
                )

                # Inspect a DataFrame, such as the interim result of data processing
                (
                    iris
                    ...
                    .check.print(fn=lambda df: df.query("sepal_width<0"), check_name="Rows with negative sepal_width")
                )
            ```

        Args:
            object: Object to print. Can be anything printable: str, int, list, another DataFrame, etc. If None, print the DataFrame's head (with `max_rows` rows).
            fn: An optional lambda function to apply to the DataFrame before printing `object`. Example: `lambda df: df.shape[0]>10`. Applied before subset.
            subset: An optional list of column names or a string name of one column to limit which columns are printed. Applied after fn.
            check_name: An optional name for the check, to be printed as preface to the result.
            max_rows: Maximum number of rows to print if object=None.

        Returns:
            The original DataFrame, unchanged.
        """
        _check_data(
            object if object else self._obj,
            check_fn=lambda data: data if object else data.head(max_rows),
            modify_fn=fn,
            subset=subset,
            check_name=check_name,
        )
        return self._obj

    def print_time_elapsed(
        self,
        start_time: float,
        lead_in: Union[str, None] = "Time elapsed",
        units: str = "auto",
    ) -> pd.DataFrame:
        """Displays the time elapsed since start_time.

        Example:
            ```python

                import pandas_checks as pdc

                start_time = pdc.start_timer()

                (
                    iris
                    ... # Do some data processing
                    .check.print_time_elapsed(start_time, "Cleaning took")

                    ... # Do more
                    .check.print_time_elapsed(start_time, "Processing total time", units="seconds") # Force units to stay in seconds

                )

                # Result: "Cleaning took: 17.298324584960938 seconds
                #         "Processing total time: 71.0400543212890625 seconds
            ```

        Args:
            start_time: The index time when the stopwatch started, which comes from the Pandas Checks start_timer()
            lead_in: Optional text to print before the elapsed time.
            units: The units in which to display the elapsed time. Allowed values: "auto", "milliseconds", "seconds", "minutes", "hours" or shorthands "ms", "s", "m", "h".

        Raises:
            ValueError: If `units` is not one of allowed values.

        Returns:
            The original DataFrame, unchanged.
        """
        print_time_elapsed(
            start_time, lead_in=lead_in, units=units
        )  # Call the public function
        return self._obj

    def reset_format(self) -> pd.DataFrame:
        """Globally restores all Pandas Checks formatting options to their default "factory" settings. Does not modify the DataFrame itself.

        Example:
            ```python
                (
                    iris
                    .check.set_format(precision=9, use_emojis=False)

                    # Print DF summary stats with precision 9 digits and no Pandas Checks emojis
                    .check.describe()

                    .check.reset_format() # Go back to default precision and emojis 🥳
                )
            ```

        Returns:
            The original DataFrame, unchanged.
        """
        reset_format()
        return self._obj

    def set_format(self, **kwargs: Any) -> pd.DataFrame:
        """Configures selected formatting options for Pandas Checks. Does not modify the DataFrame itself.

        Run pandas_checks.describe_options() to see a list of available options.

        Example:
            ```python
                (
                    iris
                    .check.set_format(precision=9, use_emojis=False)

                    # Print DF summary stats with precision 9 digits and no Pandas Checks emojis
                    .check.describe()

                    .check.reset_format() # Go back to default precision and emojis 🥳
                )
            ```

        Args:
            **kwargs: Pairs of setting name and its new value.

        Returns:
            The original DataFrame, unchanged.
        """
        set_format(**kwargs)
        return self._obj

    def set_mode(self, enable_checks: bool, enable_asserts: bool) -> pd.DataFrame:
        """Configures the operation mode for Pandas Checks globally. Does not modify the DataFrame itself.

        Example:
            ```python

                # Disable checks except keep running assertions. Same as using `.check.disable_checks()`:
                (
                    iris
                    .check.set_mode(enable_checks=False)
                    .check.describe() # This check will not be run
                    .check.assert_data(lambda s: s.shape[0]>10) #  This check will still be run
                )

                # Disable checks _and_ assertions
                (
                    iris
                    .check.set_mode(enable_checks=False, enable_asserts=False)
                )
            ```

        Args:
            enable_checks: Whether to run any Pandas Checks methods globally. Does not affect .check.assert_*().
            enable_asserts: Whether to run calls to Pandas Checks .check.assert_*() statements globally.

        Returns:
            The original DataFrame, unchanged.
        """
        set_mode(enable_checks, enable_asserts)
        return self._obj

    def shape(
        self,
        fn: Callable = lambda df: df,
        subset: Union[str, List, None] = None,
        check_name: Union[str, None] = "📐 Shape",
    ) -> pd.DataFrame:
        """Displays the Dataframe's dimensions, without modifying the DataFrame itself.

        Example:
            ```python
                (
                    iris
                    .check.shape()
                    .check.shape(fn=lambda df: df.query("sepal_length<5"), check_name="Shape of DataFrame subgroup with sepal_length<5")
                )
            ```

        Args:
            fn: An optional lambda function to apply to the DataFrame before running Pandas `shape`. Example: `lambda df: df.shape[0]>10`. Applied before subset.
            subset: An optional list of column names or a string name of one column to limit which columns are considered when printing the shape. Applied after fn.
            check_name: An optional name for the check, to be printed as preface to the result.

        Returns:
            The original DataFrame, unchanged.

        Note:
            See also .check.nrows() and .check.ncols()
        """
        _check_data(
            self._obj,
            check_fn=lambda df: df.shape,
            modify_fn=fn,
            subset=subset,
            check_name=check_name,
        )
        return self._obj

    def tail(
        self,
        n: int = 5,
        fn: Callable = lambda df: df,
        subset: Union[str, List, None] = None,
        check_name: Union[str, None] = None,
    ) -> pd.DataFrame:
        """Displays the last n rows of the DataFrame, without modifying the DataFrame itself.

        See Pandas docs for [tail()](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.tail.html) for additional usage information, including more configuration options you can pass to this Pandas Checks method.

        Example:
            ```python
                (
                    iris
                    .check.tail(10)
                )
            ```

        Args:
            n: Number of rows to show.
            fn: An optional lambda function to apply to the DataFrame before running Pandas tail(). Example: `lambda df: df.shape[0]>10`. Applied before subset.
            subset: An optional list of column names or a string name of one column to limit which columns are displayed. Applied after fn.
            check_name: An optional name for the check, to be printed as preface to the result.

        Returns:
            The original DataFrame, unchanged.
        """
        _check_data(
            self._obj,
            check_fn=lambda df: df.tail(n),
            modify_fn=fn,
            subset=subset,
            check_name=check_name if check_name else f"⬇️ Last {n} rows",
        )
        return self._obj

    def unique(
        self,
        column: str,
        fn: Callable = lambda df: df,
        check_name: Union[str, None] = None,
    ) -> pd.DataFrame:
        """Displays the unique values in a column, without modifying the DataFrame itself.

        See Pandas docs for [unique()](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.unique.html) for additional usage information, including more configuration options you can pass to this Pandas Checks method.

        Example:
            ```python
                (
                    iris
                    .check.unique("species")
                )
                # The check will print: "🌟 Unique values of species: ['setosa', 'versicolor', 'virginica']"
            ```

        Args:
            column: Column to check for unique values.
            fn: An optional lambda function to apply to the DataFrame before calling Pandas unique(). Example: `lambda df: df.shape[0]>10`. Applied before subset.
            check_name: An optional name for the check, to be printed as preface to the result.

        Returns:
            The original DataFrame, unchanged.

        Note:
            `fn` is applied to the dataframe _before_ selecting `column`. If you want to select the column before modifying it, set `column=None` and start `fn` with a column selection, i.e. `fn=lambda df: df["my_column"].stuff()`

        """
        if get_mode()["enable_checks"]:
            (
                _apply_modifications(
                    self._obj, fn=fn, subset=column
                ).check.unique(  # Apply fn, then filter to `column`  # Use SeriesChecks method
                    fn=lambda df: df,  # Identify function
                    check_name=check_name,
                )
            )
        return self._obj

    def value_counts(
        self,
        column: str,
        fn: Callable = lambda df: df,
        max_rows: int = 10,
        check_name: Union[str, None] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Displays the value counts for a column, without modifying the DataFrame itself.

        See Pandas docs for [value_counts()](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.value_counts.html) for additional usage information, including more configuration options you can pass to this Pandas Checks method.

        Example:
            ```python
                (
                    iris
                    .check.value_counts("sepal_length")
                )
            ```

        Args:
            column: Column to check for value counts.
            max_rows: Maximum number of rows to show in the value counts.
            fn: An optional lambda function to apply to the DataFrame before running Pandas value_counts(). Example: `lambda df: df.shape[0]>10`. Applied before subset.
            check_name: An optional name for the check, to be printed as preface to the result.
            **kwargs: Optional, additional arguments that are accepted by Pandas value_counts() method.

        Returns:
            The original DataFrame, unchanged.

        Note:
            `fn` is applied to the dataframe _before_ selecting `column`. If you want to select the column before modifying it, set `column=None` and start `fn` with a column selection, i.e. `fn=lambda df: df["my_column"].stuff()`
        """
        if get_mode()["enable_checks"]:
            (
                _apply_modifications(
                    self._obj, fn=fn, subset=column
                ).check.value_counts(  # Apply fn, then filter to `column``  # Use SeriesChecks method
                    max_rows=max_rows,
                    fn=lambda df: df,  # Identity function
                    check_name=check_name,
                    **kwargs,
                )
            )
        return self._obj

    def write(
        self,
        path: str,
        format: Union[str, None] = None,
        fn: Callable = lambda df: df,
        subset: Union[str, List, None] = None,
        verbose: bool = False,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Exports DataFrame to file, without modifying the DataFrame itself.

        The file format is inferred from the extension. Supports:
            - .csv
            - .feather
            - .parquet
            - .pkl # Pickle
            - .tsv # Tab-separated data file
            - .xlsx

        This functions uses the corresponding Pandas export function, such as `to_csv()` and `to_feather()`. See [Pandas docs for those corresponding export functions](https://pandas.pydata.org/docs/reference/io.html) for additional usage information, including more configuration options you can pass to this Pandas Checks method.

        Example:
            ```python
                (
                    iris

                    # Process data
                    ...

                    # Export the interim data for inspection
                    .check.write("iris_interim.xlsx")

                    # Continue processing
                    ...
                )
            ```

        Args:
            path: Path to write the file to.
            format: Optional file format to force for the export. If None, format is inferred from the file's extension in `path`.
            fn: An optional lambda function to apply to the DataFrame before exporting. Example: `lambda df: df.shape[0]>10`. Applied before subset.
            subset: An optional list of column names or a string name of one column to limit which columns are exported. Applied after fn.
            verbose: Whether to print a message when the file is written.
            **kwargs: Optional, additional keyword arguments to pass to the Pandas export function (e.g. `.to_csv()`).

        Returns:
            The original DataFrame, unchanged.

        Note:
            Exporting to some formats such as Excel, Feather, and Parquet may require you to install additional packages.
        """

        if not get_mode()["enable_checks"]:
            return self._obj
        format_clean = format.lower().replace(".", "").strip() if format else None
        data = _apply_modifications(self._obj, fn, subset)
        if path.endswith(".csv") or format_clean == "csv":
            data.to_csv(path, **kwargs)
        elif path.endswith(".feather") or format_clean == "feather":
            data.to_feather(path, **kwargs)
        elif path.endswith(".parquet") or format_clean == "parquet":
            data.to_parquet(path, **kwargs)
        elif path.endswith(".pkl") or format_clean == "pickle":
            data.to_pickle(path, **kwargs)
        elif path.endswith(".tsv") or format_clean == "tsv":
            data.to_csv(path, sep="\t", **kwargs)
        elif (
            path.endswith(".xls")
            or path.endswith(".xlsx")
            or format_clean in ["xlsx", "xls", "excel"]
        ):
            data.to_excel(path, **kwargs)
        else:
            raise AttributeError(
                f"Can't write data to file. Unknown file extension in: {path}. "
            )
        if verbose:
            _display_line(f"📦 Wrote file {path}")
        return self._obj
