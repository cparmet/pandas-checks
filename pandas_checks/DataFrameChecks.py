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
from .utils import _lambda_to_string


@pd.api.extensions.register_dataframe_accessor("check")
class DataFrameChecks:
    def __init__(self, pandas_obj: Union[pd.DataFrame, pd.Series]) -> None:
        self._obj = pandas_obj

    def assert_data(
        self,
        condition: Callable,
        subset: Union[str, List, None] = None,
        pass_message: str = " ✔️ Assertion passed ",
        fail_message: str = " ㄨ Assertion failed ",
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = DataError,
        verbose: bool = False,
    ) -> pd.DataFrame:
        """Tests whether Dataframe meets condition, optionally raise an exception if not. Does not modify the DataFrame itself.

        Args:
            condition: Assertion criteria in the form of a lambda function, such as `lambda df: df.shape[0]>10` or
            subset: Optional, which column or columns to check the condition against. Applied after fn. Subsetting can also be done within the `condition`, such as `lambda df: df['column_name'].sum()>10`
            pass_message: Message to display if the condition passes.
            fail_message: Message to display if the condition fails.
            raise_exception: Whether to raise an exception if the condition fails.
            exception_to_raise: The exception to raise if the condition fails and raise_exception is True.
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

    def columns(
        self,
        fn: Callable = lambda df: df,
        subset: Union[str, List, None] = None,
        check_name: Union[str, None] = "🏛️ Columns",
    ) -> pd.DataFrame:
        """Prints the column names of a DataFrame, without modifying the DataFrame itself.

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

        See Pandas docs for describe() for additional usage information, including more configuration options you can pass to this Pandas Checks method.

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

        See Pandas docs for dtypes for additional usage information.

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
            .check.function(fn=lambda df: df.shape[0]>10, check_name='Has at least 10 rows?')
            which will result in 'True' or 'False'

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

        See Pandas docs for head() for additional usage information.

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

        See Pandas docs for hist() for additional usage information, including more configuration options you can pass to this Pandas Checks method.

        Args:
            fn: An optional lambda function to apply to the DataFrame before running Pandas hist(). Example: `lambda df: df.shape[0]>10`. Applied before subset.
            subset: An optional list of column names or a string to select a subset of columns before running Pandas hist(). Applied after fn.
            check_name: An optional name for the check, to be printed as preface to the result.
            **kwargs: Optional, additional arguments that are accepted by Pandas hist() method.

        Returns:
            The original DataFrame, unchanged.

        Note:
            If more than one column is passed, displays a grid of histograms

            Only renders in interactive mode (IPython/Jupyter), not in terminal
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

        See Pandas docs for info() for additional usage information, including more configuration options you can pass to this Pandas Checks method.

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

        See Pandas docs for memory_usage() for additional usage information, including more configuration options you can pass to this Pandas Checks method.

        Args:
            fn: An optional lambda function to apply to the DataFrame before running Pandas memory_usage(). Example: `lambda df: df.shape[0]>10`. Applied before subset.
            subset: An optional list of column names or a string to select a subset of columns before running Pandas memory_usage(). Applied after fn.
            check_name: An optional name for the check, to be printed as preface to the result.
            **kwargs: Optional, additional arguments that are accepted by Pandas info() method.

        Returns:
            The original DataFrame, unchanged.

        Note:
            Include argument `deep=True` to get further memory usage of object dtypes in the DataFrame. See Pandas docs for memory_usage() for more info.
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

        See Pandas docs for duplicated() for additional usage information, including more configuration options you can pass to this Pandas Checks method.

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

        See Pandas docs for isna() for additional usage information.

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

        See Pandas docs for nunique() for additional usage information, including more configuration options you can pass to this Pandas Checks method.

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

        See Pandas docs for plot() for additional usage information, including more configuration options you can pass to this Pandas Checks method.

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

        Args:
            start_time: The index time when the stopwatch started, which comes from the Pandas Checks start_timer()
            lead_in: Optional text to print before the elapsed time.
            units: The units in which to display the elapsed time. Can be "auto", "seconds", "minutes", or "hours".

        Raises:
            ValueError: If `units` is not one of "auto", "seconds", "minutes", or "hours".

        Returns:
            The original DataFrame, unchanged.
        """
        print_time_elapsed(
            start_time, lead_in=lead_in, units=units
        )  # Call the public function
        return self._obj

    def reset_format(self) -> pd.DataFrame:
        """Globally restores all Pandas Checks formatting options to their default "factory" settings. Does not modify the DataFrame itself.

        Returns:
            The original DataFrame, unchanged.
        """
        reset_format()
        return self._obj

    def set_format(self, **kwargs: Any) -> pd.DataFrame:
        """Configures selected formatting options for Pandas Checks. Does not modify the DataFrame itself.

        Run pandas_checks.describe_options() to see a list of available options.

        For example, .check.set_format(check_text_tag= "h1", use_emojis=False`)
        will globally change Pandas Checks to display text results as H1 headings and remove all emojis.

        Args:
            **kwargs: Pairs of setting name and its new value.

        Returns:
            The original DataFrame, unchanged.
        """
        set_format(**kwargs)
        return self._obj

    def set_mode(self, enable_checks: bool, enable_asserts: bool) -> pd.DataFrame:
        """Configures the operation mode for Pandas Checks globally. Does not modify the DataFrame itself.

        Args:
            enable_checks: Whether to run any Pandas Checks methods globally. Does not affect .check.assert_data().
            enable_asserts: Whether to run calls to Pandas Checks .check.assert_data() statements globally.

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

        See Pandas docs for shape for additional usage information.

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

        See Pandas docs for tail() for additional usage information, including more configuration options you can pass to this Pandas Checks method.

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

        See Pandas docs for unique() for additional usage information, including more configuration options you can pass to this Pandas Checks method.

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

        See Pandas docs for value_counts() for additional usage information, including more configuration options you can pass to this Pandas Checks method.

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

        Format is inferred from path extension like .csv.

        This functions uses the corresponding Pandas export function such as to_csv(). See Pandas docs for those functions for additional usage information, including more configuration options you can pass to this Pandas Checks method.

        Args:
            path: Path to write the file to.
            format: Optional file format to force for the export. If None, format is inferred from the file's extension in `path`.
            fn: An optional lambda function to apply to the DataFrame before exporting. Example: `lambda df: df.shape[0]>10`. Applied before subset.
            subset: An optional list of column names or a string name of one column to limit which columns are exported. Applied after fn.
            verbose: Whether to print a message when the file is written.
            **kwargs: Optional, additional keyword arguments to pass to the Pandas export function (.to_csv).

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
