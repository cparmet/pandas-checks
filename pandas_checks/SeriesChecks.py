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
from .utils import _lambda_to_string


@pd.api.extensions.register_series_accessor("check")
class SeriesChecks:
    def __init__(self, pandas_obj: pd.Series) -> None:
        self._obj = pandas_obj

    def assert_data(
        self,
        condition: Callable,
        pass_message: str = " ✔️ Assertion passed ",
        fail_message: str = " ㄨ Assertion failed ",
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = DataError,
        verbose: bool = False,
    ) -> pd.Series:
        """Tests whether Series meets condition, optionally raise an exception if not. Does not modify the Series itself.

        Args:
            condition: Assertion criteria in the form of a lambda function, such as `lambda s: s.shape[0]>10`.
            pass_message: Message to display if the condition passes.
            fail_message: Message to display if the condition fails.
            raise_exception: Whether to raise an exception if the condition fails.
            exception_to_raise: The exception to raise if the condition fails and raise_exception is True.
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
        if not result:
            if raise_exception:
                raise exception_to_raise(f"{fail_message}: {condition_str}")
            else:
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
        if verbose:
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
        return self._obj

    def describe(
        self,
        fn: Callable = lambda s: s,
        check_name: Union[str, None] = "📏 Distribution",
        **kwargs: Any,
    ) -> pd.Series:
        """Displays descriptive statistics about a Series, without modifying the Series itself.

        See Pandas docs for describe() for additional usage information, including more configuration options you can pass to this Pandas Checks method.

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

        See Pandas docs for .dtype for additional usage information.

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
            .check.function(fn=lambda s: s.shape[0]>10, check_name='Has at least 10 rows?')
            which will result in 'True' or 'False'

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

        See Pandas docs for head() for additional usage information.

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

        See Pandas docs for hist() for additional usage information, including more configuration options you can pass to this Pandas Checks method.

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

        See Pandas docs for info() for additional usage information, including more configuration options you can pass to this Pandas Checks method.

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

        See Pandas docs for memory_usage() for additional usage information, including more configuration options you can pass to this Pandas Checks method.

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

        See Pandas docs for duplicated() for additional usage information, including more configuration options you can pass to this Pandas Checks method.

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

        See Pandas docs for isna() for additional usage information.

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

        See Pandas docs for nunique() for additional usage information, including more configuration options you can pass to this Pandas Checks method.

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

        See Pandas docs for plot() for additional usage information, including more configuration options you can pass to this Pandas Checks method.

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

        Args:
        start_time: The index time when the stopwatch started, which comes from the Pandas Checks start_timer()
        lead_in: Optional text to print before the elapsed time.
        units: The units in which to display the elapsed time. Can be "auto", "seconds", "minutes", or "hours".

        Raises:
            ValueError: If `units` is not one of "auto", "seconds", "minutes", or "hours".

        Returns:
            The original Series, unchanged.
        """
        print_time_elapsed(
            start_time, lead_in=lead_in, units=units
        )  # Call the public function
        return self._obj

    def reset_format(self) -> pd.Series:
        """Globally restores all Pandas Checks formatting options to their default "factory" settings. Does not modify the Series itself.

        Returns:
            The original Series, unchanged.
        """
        reset_format()
        return self._obj

    def set_format(self, **kwargs: Any) -> pd.Series:
        """Configures selected formatting options for Pandas Checks. Run pandas_checks.describe_options() to see a list of available options. Does not modify the Series itself

        For example, .check.set_format(check_text_tag= "h1", use_emojis=False`)
        will globally change Pandas Checks to display text results as H1 headings and remove all emojis.

        Args:
            **kwargs: Pairs of setting name and its new value.

        Returns:
            The original Series, unchanged.
        """
        set_format(**kwargs)
        return self._obj

    def set_mode(self, enable_checks: bool, enable_asserts: bool) -> pd.Series:
        """Configures the operation mode for Pandas Checks globally. Does not modify the Series itself.

        Args:
            enable_checks: Whether to run any Pandas Checks methods globally. Does not affect .check.assert_data().
            enable_asserts: Whether to run calls to Pandas Checks .check.assert_data() globally.

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

        See Pandas docs for `shape` for additional usage information.

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

        See Pandas docs for tail() for additional usage information.

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

        See Pandas docs for unique() for additional usage information.

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

        See Pandas docs for value_counts() for additional usage information, including more configuration options you can pass to this Pandas Checks method.

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

        Format is inferred from path extension like .csv.

        This functions uses the corresponding Pandas export function such as to_csv(). See Pandas docs for those functions for additional usage information, including more configuration options you can pass to this Pandas Checks method.

        Args:
            path: Path to write the file to.
            format: Optional file format to force for the export. If None, format is inferred from the file's extension in `path`.
            fn: An optional lambda function to apply to the Series before exporting. Example: `lambda s: s.dropna()`.
            verbose: Whether to print a message when the file is written.
            **kwargs: Optional, additional keyword arguments to pass to the Pandas export function (.to_csv).

        Returns:
            The original Series, unchanged.

        Note:
            Exporting to some formats such as Excel, Feather, and Parquet may require you to install additional packages.
        """
        (
            pd.DataFrame(_apply_modifications(self._obj, fn)).check.write(
                path=path, format=format, verbose=verbose, **kwargs
            )
        )
        return self._obj
