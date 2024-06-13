"""
Add PandasVet methods to Pandas's DataFrame class.

New nethods are accessible with pd.DataFrame.check.[method]

All new, public methods return the unchanged DataFrame. Checks do not modify the data that is returned.

Methods are also shared by the SeriesVet class.

Reminder: If adding a new method and it doesn't either A) call the SeriesVet method, B) use _check_data(),
or C) timer functions, make sure to preface the method with `if not get_mode()["enable_checks"]: return self._obj`.
That ensures the method will be disabled if the global option vet.enable_checks is set to False.
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
from .run_checks import _check_data, _modify_data
from .timer import print_time_elapsed, start_timer
from .utils import _in_terminal, _lambda_to_string


@pd.api.extensions.register_dataframe_accessor("check")
class DataFrameVet:
    def __init__(self, pandas_obj: Union[pd.DataFrame, pd.Series]) -> None:
        self._obj = pandas_obj

    def assert_data(
        self,
        condition: Union[str, Callable],
        subset: Union[str, List, None] = None,
        pass_message: str = " ✔️ Assertion passed ",
        fail_message: str = " ㄨ Assertion failed ",
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = DataError,
        verbose: bool = False,
    ) -> pd.DataFrame:
        """Test whether dataframe meets condition, optionally raise an exception if not.

        condition: can be a lambda function or an evaluable string referring to `df`, such as "df.shape[0]>10"
        """
        if not get_mode()["enable_asserts"]:
            return self._obj
        data = self._obj[subset] if subset else self._obj
        if callable(condition):
            result = condition(data)
            condition_str = _lambda_to_string(condition)
        elif isinstance(condition, str):
            result = eval(condition, {}, {"df": data})
            condition_str = condition
        else:
            raise TypeError(
                f"Argument `condition` is of unexpected type {type(condition)}"
            )
        if not result:
            if raise_exception:
                raise exception_to_raise(f"{fail_message}: {condition_str}")
            else:
                _display_line(
                    lead_in=fail_message,
                    line=condition_str,
                    colors={
                        "lead_in_text_color": pd.get_option("vet.fail_text_fg_color"),
                        "lead_in_background_color": pd.get_option(
                            "vet.fail_text_bg_color"
                        ),
                    },
                )
        if verbose:
            _display_line(
                lead_in=pass_message,
                line=condition_str,
                colors={
                    "lead_in_text_color": pd.get_option("vet.success_text_fg_color"),
                    "lead_in_background_color": pd.get_option(
                        "vet.success_text_bg_color"
                    ),
                },
            )
        return self._obj

    def columns(
        self,
        fn: Union[Callable, str] = lambda df: df,
        subset: Union[str, List, None] = None,
        check_name: Union[str, None] = "🏛️ Columns",
    ) -> pd.DataFrame:
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
        fn: Union[Callable, str] = lambda df: df,
        subset: Union[str, List, None] = None,
        check_name: Union[str, None] = "📏 Distributions",
        **kwargs: Any,
    ) -> pd.DataFrame:
        _check_data(
            self._obj,
            check_fn=lambda df: df.describe(**kwargs),
            modify_fn=fn,
            subset=subset,
            check_name=check_name,
        )
        return self._obj

    def disable_checks(self, enable_asserts: bool = True) -> pd.DataFrame:
        disable_checks(enable_asserts)
        return self._obj

    def dtypes(
        self,
        fn: Union[Callable, str] = lambda df: df,
        subset: Union[str, List, None] = None,
        check_name: Union[str, None] = "🗂️ Data types",
    ) -> pd.DataFrame:
        _check_data(
            self._obj,
            check_fn=lambda df: df.dtypes,
            modify_fn=fn,
            subset=subset,
            check_name=check_name,
        )
        return self._obj

    def enable_checks(self, enable_asserts: bool = True) -> pd.DataFrame:
        enable_checks(enable_asserts)
        return self._obj

    def function(
        self,
        fn: Union[Callable, str] = lambda df: df,
        subset: Union[str, List, None] = None,
        check_name: Union[str, None] = None,
    ) -> pd.DataFrame:
        """Apply an arbitrary function on a DataFrame and show the result.

        Example
        .check.function(fn=lambda df: df.shape[0]>10, check_name='Has at least 10 rows?')
        which will result in 'True' or 'False'

        fn: Can be a lambda function or an evaluable string referring to `df`, such as "df.shape[0]>10"
        """
        _check_data(self._obj, modify_fn=fn, subset=subset, check_name=check_name)
        return self._obj

    def get_mode(
        self, check_name: Union[str, None] = "🐼🩺 PandasVet mode"
    ) -> pd.DataFrame:
        _display_line(lead_in=check_name, line=str(get_mode()))
        return self._obj

    def head(
        self,
        n: int = 5,
        fn: Union[Callable, str] = lambda df: df,
        subset: Union[str, List, None] = None,
        check_name: Union[str, None] = None,
    ) -> pd.DataFrame:
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
        fn: Union[Callable, str] = lambda df: df,
        subset: Union[str, List, None] = [],
        check_name: Union[str, None] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Display a histogram. Only renders in IPython/Jupyter"""
        if (
            get_mode()["enable_checks"] and not _in_terminal()
        ):  # Only display if in IPython/Jupyter, or we'd just print the title
            _display_plot_title(
                check_name
                if check_name
                else "📏 Distribution"
                if subset and len(subset) == 1
                else "Distributions"
            )
            _ = _modify_data(self._obj, fn, subset).hist(**kwargs)
            _display_plot()
        return self._obj

    def info(
        self,
        fn: Union[Callable, str] = lambda df: df,
        subset: Union[str, List, None] = None,
        check_name: Union[str, None] = "ℹ️ Info",
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Don't use display or check_name comes below report"""
        if get_mode()["enable_checks"]:
            if check_name:
                _display_table_title(check_name)
            (_modify_data(self._obj, fn, subset).info(**kwargs))
        return self._obj

    def memory_usage(
        self,
        fn: Union[Callable, str] = lambda df: df,
        subset: Union[str, List, None] = None,
        check_name: Union[str, None] = "💾 Memory usage",
        **kwargs: Any,
    ) -> pd.DataFrame:
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
        fn: Union[Callable, str] = lambda df: df,
        subset: Union[str, List, None] = None,
        check_name: Union[str, None] = "🏛️ Columns",
    ) -> pd.DataFrame:
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
        fn: Union[Callable, str] = lambda df: df,
        subset: Union[str, List, None] = None,
        check_name: Union[str, None] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """kwargs are arguments to .duplicated()"""
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
        fn: Union[Callable, str] = lambda df: df,
        subset: Union[str, List, None] = None,
        by_column: bool = True,
        check_name: Union[str, None] = None,
    ) -> pd.DataFrame:
        """

        by_column = False to count rows that have any NaNs in any columns
        """
        if not get_mode()["enable_checks"]:
            return self._obj
        data = _modify_data(self._obj, fn, subset)
        na_counts = (
            data.isna().any(axis=1).sum()
            if isinstance(data, pd.DataFrame) and not by_column
            else data.isna().sum()
        )
        if not check_name:
            if isinstance(
                na_counts, (pd.DataFrame, pd.Series)
            ):  # Report result as a pandas object
                _check_data(
                    na_counts,
                    check_name=f"👻 Rows with NaNs in {subset}"
                    if subset
                    else "👻 Rows with NaNs",
                )
            else:  # Report on one line
                _display_line(
                    (
                        f"👻 Rows with NaNs in {subset}: "
                        if subset
                        else "👻 Rows with NaNs: "
                    )
                    + f"{na_counts} out of {data.shape[0]}"
                )
        else:
            _display_line(f"{check_name}: {na_counts}")
        return self._obj

    def nrows(
        self,
        fn: Union[Callable, str] = lambda df: df,
        subset: Union[str, List, None] = None,
        check_name: Union[str, None] = "☰ Rows",
    ) -> pd.DataFrame:
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
        fn: Union[Callable, str] = lambda df: df,
        check_name: Union[str, None] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Run SeriesVet method.

        Note that `fn` is applied to the dataframe _before_ filtering columns to `column`.

        If you want to apply `fn` _after_ filtering to column, set `column=None`
        and start `fn` with a column selection, i.e. `fn=lambda df: df["my_column"].stuff()`
        """
        if get_mode()["enable_checks"]:
            (
                _modify_data(
                    self._obj, fn=fn, subset=column
                ).check.nunique(  # Apply fn, then filter to `column`  # Use SeriesVet method
                    fn=lambda df: df,  # Identity function
                    check_name=check_name,
                    **kwargs,
                )
            )
        return self._obj

    def plot(
        self,
        fn: Union[Callable, str] = lambda df: df,
        subset: Union[str, List, None] = None,
        check_name: Union[str, None] = "",
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Show Pandas plot. Only renders in IPython/Jupyter
        'title' kwarg overrides check_name as plot title"""

        # Only display plot if in IPython/Jupyter. Or we'd just print its title.
        if get_mode()["enable_checks"] and not _in_terminal():
            _display_plot_title(
                check_name if "title" not in kwargs else kwargs["title"]
            )
            _ = _modify_data(self._obj, fn, subset).plot(**kwargs)
            _display_plot()
        return self._obj

    def print(
        self,
        object: Any = None,  # Anything printable: str, int, list, DataFrame, etc
        fn: Union[Callable, str] = lambda df: df,
        subset: Union[str, List, None] = None,
        check_name: Union[str, None] = None,
        max_rows: int = 10,
    ) -> pd.DataFrame:
        _check_data(
            object if object else self._obj,
            check_fn=lambda data: data if object else data.head(max_rows),
            modify_fn=fn,
            subset=subset,
            check_name=check_name,
        )
        return self._obj

    def reset_format(self) -> pd.DataFrame:
        """Re-initilaize all Pandas Vet options for formatting"""
        reset_format()
        return self._obj

    def set_format(self, **kwargs: Any) -> pd.DataFrame:
        set_format(**kwargs)
        return self._obj

    def set_mode(self, enable_checks: bool, enable_asserts: bool) -> pd.DataFrame:
        set_mode(enable_checks, enable_asserts)
        return self._obj

    def shape(
        self,
        fn: Union[Callable, str] = lambda df: df,
        subset: Union[str, List, None] = None,
        check_name: Union[str, None] = "📐 Shape",
    ) -> pd.DataFrame:
        """See nrows, ncols"""
        _check_data(
            self._obj,
            check_fn=lambda df: df.shape,
            modify_fn=fn,
            subset=subset,
            check_name=check_name,
        )
        return self._obj

    def start_timer(self, verbose: bool = False) -> pd.DataFrame:
        start_timer(verbose)  # Call the public function
        return self._obj

    def tail(
        self,
        n: int = 5,
        fn: Union[Callable, str] = lambda df: df,
        subset: Union[str, List, None] = None,
        check_name: Union[str, None] = None,
    ) -> pd.DataFrame:
        _check_data(
            self._obj,
            check_fn=lambda df: df.tail(n),
            modify_fn=fn,
            subset=subset,
            check_name=check_name if check_name else f"⬇️ Last {n} rows",
        )
        return self._obj

    def print_time_elapsed(
        self, check_name: Union[str, None] = "Time elapsed", units: str = "auto"
    ) -> pd.DataFrame:
        print_time_elapsed(
            check_name=check_name, units=units
        )  # Call the public function
        return self._obj

    def unique(
        self,
        column: str,
        fn: Union[Callable, str] = lambda df: df,
        check_name: Union[str, None] = None,
    ) -> pd.DataFrame:
        """Run SeriesVet's method

        Note that `fn` is applied to the dataframe _before_ filtering columns to `column`.

        If you want to apply `fn` _after_ filtering to column, set `column=None`
        and start `fn` with a column selection, i.e. `fn=lambda df: df["my_column"].stuff()`
        """
        if get_mode()["enable_checks"]:
            (
                _modify_data(
                    self._obj, fn=fn, subset=column
                ).check.unique(  # Apply fn, then filter to `column`  # Use SeriesVet method
                    fn=lambda df: df,  # Identify function
                    check_name=check_name,
                )
            )
        return self._obj

    def value_counts(
        self,
        column: str,
        max_rows: int = 10,
        fn: Union[Callable, str] = lambda df: df,
        check_name: Union[str, None] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Run SeriesVet's method

        Note that `fn` is applied to the dataframe _before_ filtering columns to `column`.

        If you want to apply `fn` _after_ filtering to column, set `column=None`
        and start `fn` with a column selection, i.e. `fn=lambda df: df["my_column"].stuff()`

        """
        if get_mode()["enable_checks"]:
            (
                _modify_data(
                    self._obj, fn=fn, subset=column
                ).check.value_counts(  # Apply fn, then filter to `column``  # Use SeriesVet method
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
        fn: Union[Callable, str] = lambda df: df,
        subset: Union[str, List, None] = None,
        verbose: bool = False,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Write DataFrame to file, with format inferred from path extension like .csv.

        Pass `format` argument to force

        This functions uses the corresponding Pandas export function such as to_csv().
        Exporting to some formats such as Excel, Feather, and Parquet may require additional installs.
        """

        if not get_mode()["enable_checks"]:
            return self._obj
        format_clean = format.lower().replace(".", "").strip() if format else None
        data = _modify_data(self._obj, fn, subset)
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
            _display_line("📦 Wrote file {path}")
        return self._obj
