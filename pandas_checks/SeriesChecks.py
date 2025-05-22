"""
This module installs Pandas Checks methods in the Pandas Series class.

To use Pandas Checks, don't access anything in this module directly. Instead just run `import pandas_checks` in your code. That changes what happens when you use regular Pandas Series:
    ```
    import pandas as pd
    import pandas_checks
    ```

Now new methods are accessible to Pandas Series as ".check":

    ```
    (
        pd.Series(my_data)
        .rename("new_name")
        .check.hist()           # <-- New methods available
        .dropna()
    )
    ```

All public .check methods display the result but then return the unchanged Series, so a method chain continues unbroken.
"""

from datetime import datetime, timedelta
from typing import Any, Callable, Type, Union

import matplotlib.pyplot as plt
import pandas as pd
from pandas.core.groupby.groupby import DataError

from .display import _display_line, _display_table_title
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


@pd.api.extensions.register_series_accessor("check")
class SeriesChecks:
    def __init__(self, pandas_obj: pd.Series) -> None:
        self._obj = pandas_obj

    def assert_all_nulls(
        self,
        fail_message: str = " ㄨ Assert all nulls failed ",
        pass_message: str = " ✔️ Assert all nulls passed ",
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = DataError,
        verbose: bool = False,
    ) -> pd.Series:
        """Tests whether Series has all nulls. Optionally raises an exception. Does not modify the Series itself.

        Example:
            ```python
            (
                iris
                ["sepal_length"]
                .check.assert_all_nulls()
            )

            # Will raise an exception, "ㄨ Assert all nulls failed"
            ```

            See docs for `.check.assert_data()` for examples of how to customize assertions.

        Args:
            fail_message: Message to display if the condition fails.
            pass_message: Message to display if the condition passes.
            raise_exception: Whether to raise an exception if the condition fails.
            exception_to_raise: The exception to raise if the condition fails and raise_exception is True.
            verbose: Whether to display the pass message if the condition passes.

        Returns:
            The original Series, unchanged.
        """

        self._obj.check.assert_data(
            condition=lambda s: s.isna().all().all(),
            fail_message=fail_message,
            pass_message=pass_message,
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
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = DataError,
        message_shows_condition: bool = True,
        verbose: bool = False,
    ) -> pd.Series:
        """Tests whether Series meets condition. Optionally raises an exception. Does not modify the Series itself.

        Example:
            ```python
            (
                iris
                ["sepal_length"]

                # Validate that a Series has at least 1 row:
                .check.assert_data(lambda s: s.shape[0]>0)

                # Or customize the message displayed when assert fails
                .check.assert_data(lambda df: s.shape[0]>0, "Assertion failed, Series has no rows!")

                # Or show a warning instead of raising an exception
                .check.assert_data(lambda df: s.shape[0]>0, "FYI Series has no rows", raise_exception=False)
            )
            ```

        Args:
            condition: Assertion criteria in the form of a lambda function, such as `lambda s: s.shape[0]>10`.
            fail_message: Message to display if the condition fails.
            pass_message: Message to display if the condition passes.
            raise_exception: Whether to raise an exception if the condition fails.
            exception_to_raise: The exception to raise if the condition fails and raise_exception is True.
            message_shows_condition: Whether the fail/pass message should also print the assertion criteria
            verbose: Whether to display the pass message if the condition passes.

        Returns:
            The original Series, unchanged.
        """
        if not get_mode()["enable_asserts"]:
            return self._obj
        if not callable(condition):
            raise TypeError(
                f"Expected condition to be a lambda function (callable type) but received type {type(condition)}"
            )
        result = condition(self._obj)
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
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = TypeError,
        verbose: bool = False,
    ) -> pd.Series:
        """Tests whether Series is datetime or timestamp. Optionally raises an exception. Does not modify the Series itself.

        Example:
            ```python
            (
                df
                ["datetime_col"]
                .check.assert_datetime()
            )
            ```

            See docs for `.check.assert_data()` for examples of how to customize assertions.

        Args:
            fail_message: Message to display if the condition fails. If None, will report expected vs observed type.
            pass_message: Message to display if the condition passes.
            raise_exception: Whether to raise an exception if the condition fails.
            exception_to_raise: The exception to raise if the condition fails and raise_exception is True.
            verbose: Whether to display the pass message if the condition passes.

        Returns:
            The original Series, unchanged.
        """

        self._obj.check.assert_type(
            dtype=datetime,
            fail_message=fail_message,
            pass_message=pass_message,
            raise_exception=raise_exception,
            exception_to_raise=exception_to_raise,
            verbose=verbose,
        )
        return self._obj

    def assert_float(
        self,
        fail_message: Union[str, None] = None,
        pass_message: str = " ✔️ Assert float passed ",
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = TypeError,
        verbose: bool = False,
    ) -> pd.Series:
        """Tests whether Series is floats. Optionally raises an exception. Does not modify the Series itself.

        Example:
            ```python
            (
                df
                ["float_col"]
                .check.assert_float()
            )
            ```

            See docs for `.check.assert_data()` for examples of how to customize assertions.

        Args:
            fail_message: Message to display if the condition fails. If None, will report expected vs observed type.
            pass_message: Message to display if the condition passes.
            raise_exception: Whether to raise an exception if the condition fails.
            exception_to_raise: The exception to raise if the condition fails and raise_exception is True.
            verbose: Whether to display the pass message if the condition passes.

        Returns:
            The original Series, unchanged.
        """

        self._obj.check.assert_type(
            dtype=float,
            fail_message=fail_message,
            pass_message=pass_message,
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
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = DataError,
        verbose: bool = False,
    ) -> pd.Series:
        """Tests whether Series is > or >= a minimum threshold. Optionally raises an exception. Does not modify the Series itself.

        Example:
            ```python
            (
                iris
                ["sepal_length"]
                # Validate that the Series is always >= 0
                .check.assert_greater_than(0, or_equal_to=True)
            )
            ```

            See docs for `.check.assert_data()` for examples of how to customize assertions.

        Args:
            min: the minimum value to compare Series to. Accepts any type that can be used in >, such as int, float, str, datetime
            fail_message: Message to display if the condition fails.
            pass_message: Message to display if the condition passes.
            or_equal_to: whether to test for >= min (True) or > min (False)
            raise_exception: Whether to raise an exception if the condition fails.
            exception_to_raise: The exception to raise if the condition fails and raise_exception is True.
            verbose: Whether to display the pass message if the condition passes.

        Returns:
            The original Series, unchanged.
        """
        if or_equal_to:
            min_fn = lambda s: (s >= min).all().all()
        else:
            min_fn = lambda s: (s > min).all().all()

        self._obj.check.assert_data(
            condition=min_fn,
            fail_message=fail_message,
            pass_message=pass_message,
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
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = TypeError,
        verbose: bool = False,
    ) -> pd.Series:
        """Tests whether Series is integers. Optionally raises an exception. Does not modify the Series itself.

        Example:
            ```python
            (
                df
                ["int_col"]
                .check.assert_int()
            )
            ```

            See docs for `.check.assert_data()` for examples of how to customize assertions.

        Args:
            fail_message: Message to display if the condition fails. If None, will report expected vs observed type.
            pass_message: Message to display if the condition passes.
            raise_exception: Whether to raise an exception if the condition fails.
            exception_to_raise: The exception to raise if the condition fails and raise_exception is True.
            verbose: Whether to display the pass message if the condition passes.

        Returns:
            The original Series, unchanged.
        """

        self._obj.check.assert_type(
            dtype=int,
            fail_message=fail_message,
            pass_message=pass_message,
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
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = DataError,
        verbose: bool = False,
    ) -> pd.Series:
        """Tests whether all values in Series are < or <= a maximum threshold. Optionally raises an exception. Does not modify the Series itself.

        Example:
            ```python
            (
                iris
                ["sepal_length"]

                # Validate that sepal_length is always < 1000
                .check.assert_less_than(1000)

                # Validate that it's always <= 1000
                .check.assert_less_than(1000, or_equal_to=True)
            )
            ```

            See docs for `.check.assert_data()` for examples of how to customize assertions.

        Args:
            max: the max value to compare Series to. Accepts any type that can be used in <, such as int, float, str, datetime
            fail_message: Message to display if the condition fails.
            pass_message: Message to display if the condition passes.
            or_equal_to: whether to test for <= max (True) or < max (False)
            raise_exception: Whether to raise an exception if the condition fails.
            exception_to_raise: The exception to raise if the condition fails and raise_exception is True.
            verbose: Whether to display the pass message if the condition passes.

        Returns:
            The original Series, unchanged.
        """
        if or_equal_to:
            max_fn = lambda s: (s <= max).all().all()
        else:
            max_fn = lambda s: (s < max).all().all()

        self._obj.check.assert_data(
            condition=max_fn,
            fail_message=fail_message,
            pass_message=pass_message,
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
        assert_no_nulls: bool = True,
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = DataError,
        verbose: bool = False,
    ) -> pd.Series:
        """Tests whether Series has all negative values. Optionally raises an exception. Does not modify the Series itself.

        Example:
            ```python
            (
                df
                ["column_name"]
                .check.assert_negative()
            )
            ```

            See docs for `.check.assert_data()` for examples of how to customize assertions.

        Args:
            fail_message: Message to display if the condition fails.
            pass_message: Message to display if the condition passes.
            assert_no_nulls: Whether to also enforce that data has no nulls.
            raise_exception: Whether to raise an exception if the condition fails.
            exception_to_raise: The exception to raise if the condition fails and raise_exception is True.
            verbose: Whether to display the pass message if the condition passes.

        Returns:
            The original Series, unchanged.
        """

        if assert_no_nulls:
            if _has_nulls(
                data=self._obj,
                fail_message=fail_message,
                raise_exception=raise_exception,
                exception_to_raise=exception_to_raise,
            ):
                # _has_nulls() will raise exception or print failure
                return self._obj

        self._obj.dropna().check.assert_data(
            condition=lambda s: (s < 0).all().all(),
            fail_message=fail_message,
            pass_message=pass_message,
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
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = DataError,
        verbose: bool = False,
    ) -> pd.Series:
        """Tests whether Series has no nulls. Optionally raises an exception. Does not modify the Series itself.

        Example:
            ```python
            (
                ["sepal_length"]
                .check.assert_no_nulls()
            )
            ```

            See docs for `.check.assert_data()` for examples of how to customize assertions.

        Args:
            fail_message: Message to display if the condition fails.
            pass_message: Message to display if the condition passes.
            raise_exception: Whether to raise an exception if the condition fails.
            exception_to_raise: The exception to raise if the condition fails and raise_exception is True.
            verbose: Whether to display the pass message if the condition passes.

        Returns:
            The original Series, unchanged.
        """

        self._obj.check.assert_data(
            condition=lambda s: s.isna().any().any() == False,
            fail_message=fail_message,
            pass_message=pass_message,
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
        """Tests whether Series has a given number of rows. Optionally raises an exception. Does not modify the Series itself.

        Example:
            ```python
            (
                iris
                ["species"]
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
            The original Series, unchanged.
        """

        self._obj.check.assert_data(
            condition=lambda s: s.shape[0] == nrows,
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
        assert_no_nulls: bool = True,
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = DataError,
        verbose: bool = False,
    ) -> pd.Series:
        """Tests whether Series has all positive values. Optionally raises an exception. Does not modify the Series itself.

        Example:
            ```python
            (
                iris
                ["sepal_length"]
                .check.assert_positive()
            )
            ```

            See docs for `.check.assert_data()` for examples of how to customize assertions.

        Args:
            fail_message: Message to display if the condition fails.
            pass_message: Message to display if the condition passes.
            assert_no_nulls: Whether to also enforce that data has no nulls.
            raise_exception: Whether to raise an exception if the condition fails.
            exception_to_raise: The exception to raise if the condition fails and raise_exception is True.
            verbose: Whether to display the pass message if the condition passes.

        Returns:
            The original Series, unchanged.
        """
        if assert_no_nulls:
            if _has_nulls(
                data=self._obj,
                fail_message=fail_message,
                raise_exception=raise_exception,
                exception_to_raise=exception_to_raise,
            ):
                # _has_nulls() will raise exception or print failure
                return self._obj

        self._obj.dropna().check.assert_data(
            condition=lambda s: (s > 0).all().all(),
            pass_message=pass_message,
            fail_message=fail_message,
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
        """Tests whether Series has the same number of rows as another DataFrame/Series has.

        Optionally raises an exception. Does not modify the Series itself.

        Example:
            ```python
            (
                df1
                ["column"]
                .check.assert_same_nrows(df2)
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
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = TypeError,
        verbose: bool = False,
    ) -> pd.Series:
        """Tests whether Series is strings. Optionally raises an exception. Does not modify the Series itself.

        Example:
            ```python
            (
                iris
                ["species"]
                .check.assert_str()
            )
            ```

            See docs for `.check.assert_data()` for examples of how to customize assertions.

        Args:
            fail_message: Message to display if the condition fails. If None, will report expected vs observed type.
            pass_message: Message to display if the condition passes.
            raise_exception: Whether to raise an exception if the condition fails.
            exception_to_raise: The exception to raise if the condition fails and raise_exception is True.
            verbose: Whether to display the pass message if the condition passes.

        Returns:
            The original Series, unchanged.
        """

        self._obj.check.assert_type(
            dtype=str,
            fail_message=fail_message,
            pass_message=pass_message,
            raise_exception=raise_exception,
            exception_to_raise=exception_to_raise,
            verbose=verbose,
        )
        return self._obj

    def assert_timedelta(
        self,
        fail_message: Union[str, None] = None,
        pass_message: str = " ✔️ Assert timedelta passed ",
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = TypeError,
        verbose: bool = False,
    ) -> pd.Series:
        """Tests whether Series is of type timedelta. Optionally raises an exception. Does not modify the Series itself.

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
            raise_exception: Whether to raise an exception if the condition fails.
            exception_to_raise: The exception to raise if the condition fails and raise_exception is True.
            verbose: Whether to display the pass message if the condition passes.

        Returns:
            The original Series, unchanged.
        """

        self._obj.check.assert_type(
            dtype=timedelta,
            fail_message=fail_message,
            pass_message=pass_message,
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
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = TypeError,
        verbose: bool = False,
    ) -> pd.Series:
        """Tests whether Series meets type assumption. Optionally raises an exception. Does not modify the Series itself.

        Example:
            ```python
            # Validate that a column of mixed types has overall type `object`:
            (
                iris
                ["column_with_mixed_types"]
                .check.assert_type(object)
            )
            ```

            See docs for `.check.assert_data()` for examples of how to customize assertions.

        Args:
            dtype: The required variable type
            fail_message: Message to display if the condition fails. If None, will report expected vs observed type.
            pass_message: Message to display if the condition passes.
            raise_exception: Whether to raise an exception if the condition fails.
            exception_to_raise: The exception to raise if the condition fails and raise_exception is True.
            verbose: Whether to display the pass message if the condition passes.

        Returns:
            The original Series, unchanged.
        """

        found_dtype = self._obj.dtypes
        if not fail_message:
            dtype_clean = (
                str(dtype).replace("<class", "").replace(">", "").replace("'", "")
            )  # <class > types will get blanked out in our HTML display
            fail_message = (
                f" ㄨ Assert type failed: expected {dtype_clean}, got {found_dtype}"
            )
        self._obj.check.assert_data(
            condition=lambda s: _is_type(s, dtype),
            fail_message=fail_message,
            pass_message=pass_message,
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
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = DataError,
        verbose: bool = False,
    ) -> pd.Series:
        """Validates that a Series has no duplicate values. Optionally raises an exception. Does not modify the Series itself.

        Example:
            ```python
            (
                df
                ["id_column"]
                .check.assert_unique()
            )
            ```

            See docs for `.check.assert_data()` for examples of how to customize assertions.

        Args:
            fail_message: Message to display if the condition fails.
            pass_message: Message to display if the condition passes.
            raise_exception: Whether to raise an exception if the condition fails.
            exception_to_raise: The exception to raise if the condition fails and raise_exception is True.
            verbose: Whether to display the pass message if the condition passes.

        Returns:
            The original Series, unchanged.
        """

        self._obj.check.assert_data(
            condition=lambda s: s.duplicated().sum() == 0,
            fail_message=fail_message,
            pass_message=pass_message,
            raise_exception=raise_exception,
            exception_to_raise=exception_to_raise,
            message_shows_condition=False,
            verbose=verbose,
        )
        return self._obj

    def describe(
        self,
        fn: Callable = lambda s: s,
        check_name: Union[str, None] = "📏 Distribution",
        **kwargs: Any,
    ) -> pd.Series:
        """Displays descriptive statistics about a Series, without modifying the Series itself.

        See Pandas docs for [describe()](https://pandas.pydata.org/docs/reference/api/pandas.Series.describe.html) for additional usage information, including more configuration options you can pass to this Pandas Checks method.

        Example:
            ```python
            (
                iris
                ["sepal_length"]
                .check.describe()
            )
            ```

        Args:
            fn: An optional lambda function to apply to the Series before running Pandas describe(). Example: `lambda s: s.dropna()`.
            check_name: An optional name for the check to preface the result with.
            **kwargs: Optional, additional arguments that are accepted by Pandas describe() method.

        Returns:
            The original Series, unchanged.
        """
        pd.DataFrame(_apply_modifications(self._obj, fn)).check.describe(
            check_name=check_name, **kwargs
        )
        return self._obj

    def disable_checks(self, enable_asserts: bool = True) -> pd.Series:
        """Turns off Pandas Checks globally, such as in production mode. Calls to .check functions will not be run. Does not modify the Series itself.

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

        Args
            enable_assert: Optionally, whether to also enable or disable assert statements

        Returns:
            The original Series, unchanged.
        """
        disable_checks(enable_asserts)
        return self._obj

    def dtype(
        self,
        fn: Callable = lambda s: s,
        check_name: Union[str, None] = "🗂️ Data type",
    ) -> pd.Series:
        """Displays the data type of a Series, without modifying the Series itself.

        Example:
            ```python
            (
                iris
                ["sepal_length"]
                .check.dtype()
            )
            ```

        Args:
            fn: An optional lambda function to apply to the Series before running Pandas dtype. Example: `lambda s: s.dropna()`.
            check_name: An optional name for the check to preface the result with.

        Returns:
            The original Series, unchanged.
        """
        _check_data(
            self._obj,
            check_fn=lambda s: s.dtype,
            modify_fn=fn,
            check_name=check_name,
        )
        return self._obj

    def enable_checks(self, enable_asserts: bool = True) -> pd.Series:
        """Globally enables Pandas Checks. Subequent calls to .check methods will be run. Does not modify the Series itself.

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
            The original Series, unchanged.
        """
        enable_checks(enable_asserts)
        return self._obj

    def function(
        self,
        fn: Callable = lambda s: s,
        check_name: Union[str, None] = None,
    ) -> pd.Series:
        """Applies an arbitrary function on a Series and shows the result, without modifying the Series itself.

        Example:
            ```python
            (
                iris
                .check.function(fn=lambda s: s.shape[0]>10, check_name='Has at least 10 rows?')
            )
            # Will return "True"
            ```

        Args:
            fn: The lambda function to apply to the Series. Example: `lambda s: s.dropna()`.
            check_name: An optional name for the check to preface the result with.

        Returns:
            The original Series, unchanged.
        """
        _check_data(self._obj, modify_fn=fn, check_name=check_name)
        return self._obj

    def get_mode(
        self, check_name: Union[str, None] = "⚙️ Pandas Checks mode"
    ) -> pd.Series:
        """Displays the current values of Pandas Checks global options enable_checks and enable_asserts. Does not modify the Series itself.

        Example:
            ```python
            (
                iris
                ["sepal_length"]
                .check.get_mode()
            )

            # The check will print: "🐼🩺 Pandas Checks mode: {'enable_checks': True, 'enable_asserts': True}"
            ```

        Args:
            check_name: An optional name for the check. Will be used as a preface the printed result.

        Returns:
            The original Series, unchanged.
        """
        pd.DataFrame(self._obj).check.get_mode(check_name=check_name)
        return self._obj

    def head(
        self,
        n: int = 5,
        fn: Callable = lambda s: s,
        check_name: Union[str, None] = None,
    ) -> pd.Series:
        """Displays the first n rows of a Series, without modifying the Series itself.

        See Pandas docs for [head()](https://pandas.pydata.org/docs/reference/api/pandas.Series.head.html) for additional usage information.

        Example:
            ```python
            (
                iris
                ["sepal_length"]
                .check.head(10)
            )
            ```

        Args:
            n: The number of rows to display.
            fn: An optional lambda function to apply to the Series before running Pandas head(). Example: `lambda s: s.dropna()`.
            check_name: An optional name for the check, to be printed as preface to the result.

        Returns:
            The original Series, unchanged.
        """
        pd.DataFrame(_apply_modifications(self._obj, fn)).check.head(
            n=n, check_name=check_name
        )
        return self._obj

    def hist(
        self,
        fn: Callable = lambda s: s,
        check_name: Union[str, None] = None,
        **kwargs: Any,
    ) -> pd.Series:
        """Displays a histogram for the Series's distribution, without modifying the Series itself.

        See Pandas docs for [hist()](https://pandas.pydata.org/docs/reference/api/pandas.Series.hist.html) for additional usage information, including more configuration options you can pass to this Pandas Checks method.

        Example:
            ```python
            (
                iris
                ["sepal_length"]
                .check.hist()
            )
            ```

        Args:
            fn: An optional lambda function to apply to the Series before running Pandas head(). Example: `lambda s: s.dropna()`.
            check_name: An optional name for the check, to be printed as preface to the result.
            **kwargs: Optional, additional arguments that are accepted by Pandas hist() method.

        Returns:
            The original Series, unchanged.

        Note:
            Plots are only displayed when code is run in IPython/Jupyter, not in terminal.
        """
        pd.DataFrame(_apply_modifications(self._obj, fn)).check.hist(
            check_name=check_name, subset=[], **kwargs
        )
        return self._obj

    def info(
        self,
        fn: Callable = lambda s: s,
        check_name: Union[str, None] = "ℹ️ Series info",
        **kwargs: Any,
    ) -> pd.Series:
        """Displays summary information about a Series, without modifying the Series itself.

        See Pandas docs for [info()](https://pandas.pydata.org/docs/reference/api/pandas.Series.info.html) for additional usage information, including more configuration options you can pass to this Pandas Checks method.

        Example:
            ```python
            (
                iris
                ["sepal_length"]
                .check.info()
            )
            ```

        Args:
            fn: An optional lambda function to apply to the Series before running Pandas info(). Example: `lambda s: s.dropna()`.
            check_name: An optional name for the check, to be printed as preface to the result.
            **kwargs: Optional, additional arguments that are accepted by Pandas info() method.

        Returns:
            The original Series, unchanged.
        """
        if get_mode()["enable_checks"]:
            if check_name:
                _display_table_title(check_name)
            _apply_modifications(self._obj, fn).info(**kwargs)
        return self._obj

    def memory_usage(
        self,
        fn: Callable = lambda s: s,
        check_name: Union[str, None] = "💾 Memory usage",
        **kwargs: Any,
    ) -> pd.Series:
        """Displays the memory footprint of a Series, without modifying the Series itself.

        See Pandas docs for [memory_usage()](https://pandas.pydata.org/docs/reference/api/pandas.Series.memory_usage.html) for additional usage information, including more configuration options you can pass to this Pandas Checks method.

        Example:
            ```python
            (
                iris
                ["sepal_length"]
                .check.memory_usage()
            )
            ```

        Args:
            fn: An optional lambda function to apply to the Series before running Pandas memory_usage(). Example: `lambda s: s.dropna()`.
            check_name: An optional name for the check, to be printed as preface to the result.
            **kwargs: Optional, additional arguments that are accepted by Pandas memory_usage() method.

        Returns:
            The original Series, unchanged.

        Note:
            Include argument `deep=True` to get further memory usage of object dtypes. See Pandas docs for memory_usage() for more info.
        """
        pd.DataFrame(_apply_modifications(self._obj, fn)).check.memory_usage(
            check_name=check_name, **kwargs
        )
        return self._obj

    def ndups(
        self,
        fn: Callable = lambda s: s,
        check_name: Union[str, None] = None,
        **kwargs: Any,
    ) -> pd.Series:
        """Displays the number of duplicated rows in the Series, without modifying the Series itself.

        See Pandas docs for [duplicated()](https://pandas.pydata.org/docs/reference/api/pandas.Series.duplicated.html) for additional usage information, including more configuration options (the `keep` argument) you can pass to this Pandas Checks method.

        Example:
            ```python
            (
                iris
                ["sepal_length"]
                .check.ndups()
            )
            ```

        Args:
            fn: An optional lambda function to apply to the Series before counting the number of duplicates. Example: `lambda s: s.dropna()`.
            check_name: An optional name for the check, to be printed as preface to the result.
            **kwargs: Optional, additional arguments that are accepted by Pandas duplicated() method.

        Returns:
            The original Series, unchanged.
        """
        pd.DataFrame(_apply_modifications(self._obj, fn)).check.ndups(
            fn, check_name=check_name, **kwargs
        )
        return self._obj

    def nnulls(
        self,
        fn: Callable = lambda s: s,
        check_name: Union[str, None] = "👻 Rows with NaNs",
    ) -> pd.Series:
        """Displays the number of rows with null values in the Series, without modifying the Series itself.

        See Pandas docs for [isna()](https://pandas.pydata.org/docs/reference/api/pandas.Series.isna.html) for additional usage information.

        Example:
            ```python
            (
                iris
                ["sepal_length"]
                .check.nnulls()
            )
            ```

        Args:
            fn: An optional lambda function to apply to the Series before counting rows with nulls. Example: `lambda s: s.dropna()`.
            check_name: An optional name for the check, to be printed as preface to the result.

        Returns:
            The original Series, unchanged.
        """
        pd.DataFrame(_apply_modifications(self._obj, fn)).check.nnulls(
            by_column=False, check_name=check_name
        )
        return self._obj

    def nrows(
        self,
        fn: Callable = lambda s: s,
        check_name: Union[str, None] = "☰ Rows",
    ) -> pd.Series:
        """Displays the number of rows in a Series, without modifying the Series itself.

        Example:
            ```python
            (
                iris
                ["sepal_width"]
                .check.nrows()
            )
            ```

        Args:
            fn: An optional lambda function to apply to the Series before counting the number of rows. Example: `lambda s: s.dropna()`.
            check_name: An optional name for the check, to be printed as preface to the result.

        Returns:
            The original Series, unchanged.
        """
        pd.DataFrame(_apply_modifications(self._obj, fn)).check.nrows(
            check_name=check_name
        )
        return self._obj

    def nunique(
        self,
        fn: Callable = lambda s: s,
        check_name: Union[str, None] = None,
        **kwargs: Any,
    ) -> pd.Series:
        """Displays the number of unique rows in a Series, without modifying the Series itself.

        See Pandas docs for [nunique()](https://pandas.pydata.org/docs/reference/api/pandas.Series.nunique.html) for additional usage information, including more configuration options (the `dropna` argument) you can pass to this Pandas Checks method.

        Example:
            ```python
            (
                iris
                ["sepal_width"]
                .check.nunique()
            )
            ```

        Args:
            fn: An optional lambda function to apply to the Series before running Pandas nunique(). Example: `lambda s: s.dropna()`.
            check_name: An optional name for the check, to be printed as preface to the result.
            **kwargs: Optional, additional arguments that are accepted by Pandas nunique() method.

        Returns:
            The original Series, unchanged.
        """
        _check_data(
            self._obj,
            check_fn=lambda s: s.nunique(**kwargs),
            modify_fn=fn,
            check_name=check_name
            if check_name
            else f"🌟 Unique values in {self._obj.name if self._obj.name else 'series'}",
        )
        return self._obj

    def plot(
        self,
        fn: Callable = lambda s: s,
        check_name: Union[str, None] = "",
        **kwargs: Any,
    ) -> pd.Series:
        """Displays a plot of the Series, without modifying the Series itself.

        See Pandas docs for [plot()](https://pandas.pydata.org/docs/reference/api/pandas.Series.plot.html) for additional usage information, including more configuration options you can pass to this Pandas Checks method.

        Example:
            ```python
            # Visualize the distribution of a Series with a box plot:
            (
                iris
                ["sepal_width"]
                .check.plot(kind="box", title="Distribution of sepal width")
            )
            ```

        Args:
            fn: An optional lambda function to apply to the Series before running Pandas plot(). Example: `lambda s: s.dropna()`.
            check_name: An optional title for the plot.
            **kwargs: Optional, additional arguments that are accepted by Pandas plot() method.

        Returns:
            The original Series, unchanged.

        Note:
            Plots are only displayed when code is run in IPython/Jupyter, not in terminal.

            If you pass a 'title' kwarg, it becomes the plot title, overriding check_name
        """
        pd.DataFrame(_apply_modifications(self._obj, fn)).check.plot(
            fn, check_name=check_name, **kwargs
        )
        return self._obj

    def print(
        self,
        object: Any = None,  # Anything printable: str, int, list, DataFrame, etc
        fn: Callable = lambda s: s,
        check_name: Union[str, None] = None,
        max_rows: int = 10,
    ) -> pd.Series:
        """Displays text, another object, or (by default) the current DataFrame's head. Does not modify the Series itself.

        Example:
            ```python
            (
                iris
                ["sepal_width"]

                # Print messages such as milestones
                .check.print("Starting data cleaning..."")
                ...

                # Inspect a Series, such as the interim result of data processing
                .check.print(fn=lambda s: s[s<0], check_name="Negative values of sepal_width") # Will print those values if they exist
            )
            ```

        Args:
            object: Object to print. Can be anything printable: str, int, list, another DataFrame, etc. If None, print the Series's head (with `max_rows` rows).
            fn: An optional lambda function to apply to the Series before printing `object`. Example: `lambda s: s.dropna()`.
            check_name: An optional name for the check, to be printed as preface to the result.
            max_rows: Maximum number of rows to print if object=None.

        Returns:
            The original Series, unchanged.
        """
        pd.DataFrame(_apply_modifications(self._obj, fn)).check.print(
            object=object, check_name=check_name, max_rows=max_rows
        )
        return self._obj

    def print_time_elapsed(
        self,
        start_time: float,
        lead_in: Union[str, None] = "Time elapsed",
        units: str = "auto",
    ) -> pd.Series:
        """Displays the time elapsed since start_time.

        Example:
            ```python
            import pandas_checks as pdc

            start_time = pdc.start_timer()

            (
                iris
                ["species"]
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
            The original Series, unchanged.
        """
        print_time_elapsed(
            start_time, lead_in=lead_in, units=units
        )  # Call the public function
        return self._obj

    def reset_format(self) -> pd.Series:
        """Globally restores all Pandas Checks formatting options to their default "factory" settings. Does not modify the Series itself.

        Example:
            ```python
            (
                iris
                ["sepal_width"]
                .check.set_format(precision=9, use_emojis=False)

                # Print Series summary stats with precision 9 digits and no Pandas Checks emojis
                .check.describe()

                .check.reset_format() # Go back to default precision and emojis 🥳
            )
            ```

        Returns:
            The original Series, unchanged.
        """
        reset_format()
        return self._obj

    def set_format(self, **kwargs: Any) -> pd.Series:
        """Configures selected formatting options for Pandas Checks. Does not modify the Series itself.

        Run pandas_checks.describe_options() to see a list of available options.

        See .check.reset_format() to restore defaults.

        Example:
            ```python
            (
                iris
                ["sepal_width"]
                .check.set_format(precision=9, use_emojis=False)

                # Print Series summary stats with precision 9 digits and no Pandas Checks emojis
                .check.describe()

                .check.reset_format() # Go back to default precision and emojis 🥳
            )
            ```

        Args:
            **kwargs: Pairs of setting name and its new value.

        Returns:
            The original Series, unchanged.
        """
        set_format(**kwargs)
        return self._obj

    def set_mode(self, enable_checks: bool, enable_asserts: bool) -> pd.Series:
        """Configures the operation mode for Pandas Checks globally. Does not modify the Series itself.

        Example:
            ```python
            (
                iris
                ["sepal_width"]

                # Disable checks except keep running assertions. Same as using `.check.disable_checks()`:
                .check.set_mode(enable_checks=False)
                .check.describe() # This check will not be run
                .check.assert_data(lambda s: s.shape[0]>10) #  This check will still be run

                # Disable checks _and_ assertions
                .check.set_mode(enable_checks=False, enable_asserts=False)
            )
            ```

        Args:
            enable_checks: Whether to run any Pandas Checks methods globally. Does not affect .check.assert_*() calls.
            enable_asserts: Whether to run calls to Pandas Checks .check.assert_*() globally.

        Returns:
            The original Series, unchanged.
        """
        set_mode(enable_checks, enable_asserts)
        return self._obj

    def shape(
        self,
        fn: Callable = lambda s: s,
        check_name: Union[str, None] = "📐 Shape",
    ) -> pd.Series:
        """Displays the Series's dimensions, without modifying the Series itself.

        Example:
            ```python
            (
                iris
                ["sepal_width"]
                .check.shape()
                .check.shape(fn=lambda s: s[s<5]), check_name="Shape of sepal_width series with values <5")
            )
            ```

        Args:
            fn: An optional lambda function to apply to the Series before running Pandas `shape`. Example: `lambda s: s.dropna()`.
            check_name: An optional name for the check, to be printed as preface to the result.

        Returns:
            The original Series, unchanged.

        Note:
            See also .check.nrows()
        """

        _check_data(
            self._obj,
            check_fn=lambda s: s.shape,
            modify_fn=fn,
            check_name=check_name,
        )
        return self._obj

    def tail(
        self,
        n: int = 5,
        fn: Callable = lambda s: s,
        check_name: Union[str, None] = None,
    ) -> pd.Series:
        """Displays the last n rows of the Series, without modifying the Series itself.

        See Pandas docs for [tail()](https://pandas.pydata.org/docs/reference/api/pandas.Series.tail.html) for additional usage information.

        Example:
            ```python
            (
                iris
                .check.tail(10)
            )
            ```

        Args:
            n: Number of rows to show.
            fn: An optional lambda function to apply to the Series before running Pandas tail(). Example: `lambda s: s.dropna()`.
            check_name: An optional name for the check, to be printed as preface to the result.

        Returns:
            The original Series, unchanged.
        """
        pd.DataFrame(_apply_modifications(self._obj, fn)).check.tail(
            n=n, check_name=check_name
        )
        return self._obj

    def unique(
        self,
        fn: Callable = lambda s: s,
        check_name: Union[str, None] = None,
    ) -> pd.Series:
        """Displays the unique values in a Series, without modifying the Series itself.

        See Pandas docs for [unique()](https://pandas.pydata.org/docs/reference/api/pandas.Series.unique.html) for additional usage information.

        Example:
            ```python
            (
                iris
                ["species"]
                .check.unique()
            )
            # The check will print: "🌟 Unique values of species: ['setosa', 'versicolor', 'virginica']"
            ```

        Args:
            fn: An optional lambda function to apply to the Series before running Pandas unique(). Example: `lambda s: s.dropna()`.
            check_name: An optional name for the check, to be printed as preface to the result.

        Returns:
            The original Series, unchanged.
        """
        _check_data(
            self._obj,
            check_fn=lambda s: s.unique().tolist(),
            modify_fn=fn,
            check_name=check_name
            if check_name
            else f"🌟 Unique values of {self._obj.name if self._obj.name else 'series'}",
        )
        return self._obj

    def value_counts(
        self,
        fn: Callable = lambda s: s,
        max_rows: int = 10,
        check_name: Union[str, None] = None,
        **kwargs: Any,
    ) -> pd.Series:
        """Displays the value counts for a Series, without modifying the Series itself.

        See Pandas docs for [value_counts()](https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html) for additional usage information, including more configuration options you can pass to this Pandas Checks method.

        Example:
            ```python
            (
                iris
                ["sepal_length"]
                .check.value_counts()
            )
            ```

        Args:
            max_rows: Maximum number of rows to show in the value counts.
            fn: An optional lambda function to apply to the Series before running Pandas value_counts(). Example: `lambda s: s.dropna()`.
            check_name: An optional name for the check, to be printed as preface to the result.
            **kwargs: Optional, additional arguments that are accepted by Pandas value_counts() method.

        Returns:
            The original Series, unchanged.
        """
        _check_data(
            self._obj,
            check_fn=lambda s: s.value_counts(**kwargs).head(max_rows),
            modify_fn=fn,
            check_name=check_name
            if check_name
            else f"🧮 Value counts, first {max_rows} values"
            if max_rows
            else f"🧮 Value counts",
        )
        return self._obj

    def write(
        self,
        path: str,
        format: Union[str, None] = None,
        fn: Callable = lambda s: s,
        verbose: bool = False,
        **kwargs: Any,
    ) -> pd.Series:
        """Exports Series to file, without modifying the Series itself.

        The file format is inferred from the extension. Supports:
            - .csv
            - .feather
            - .parquet
            - .pkl # Pickle
            - .tsv # Tab-separated data file
            - .xlsx

        This functions uses the corresponding Pandas export function such as to_csv() and to_feather(). See [Pandas docs for those corresponding export functions](https://pandas.pydata.org/docs/reference/io.html) for additional usage information, including more configuration options you can pass to this Pandas Checks method.

        Note:
            Exporting to some formats such as Excel, Feather, and Parquet may require you to install additional packages.

        Example:
            ```python
            (
                iris
                ["sepal_length"]

                # Process data
                ...

                # Export the interim data for inspection
                .check.write("sepal_length_interim.xlsx")

                # Continue processing
                ...
            )
            ```

        Args:
            path: Path to write the file to.
            format: Optional file format to force for the export. If None, format is inferred from the file's extension in `path`.
            fn: An optional lambda function to apply to the Series before exporting. Example: `lambda s: s.dropna()`.
            verbose: Whether to print a message when the file is written.
            **kwargs: Optional, additional keyword arguments to pass to the Pandas export function (e.g. `.to_csv()`).

        Returns:
            The original Series, unchanged.

        """
        (
            pd.DataFrame(_apply_modifications(self._obj, fn)).check.write(
                path=path, format=format, verbose=verbose, **kwargs
            )
        )
        return self._obj
