"""
Add PandasVet methods to Pandas's Series class.

All new, public methods return the unchanged Series. Checks do not modify the data that is returned.

These methods call DataFrameVet methods whenever possible, setting subset=None.

Reminder: If adding a new method and it doesn't either A) call the DataFrameVet method, B) use _check_data(),
or C) timer functions, make sure to preface the method with `if not get_mode()["enable_checks"]: return self._obj`.
That ensures the method will be disabled if the global option vet.enable_checks is set to False.
"""

from typing import Any, Callable, Type, Union

import matplotlib.pyplot as plt
import pandas as pd
from pandas.core.groupby.groupby import DataError

from .options import disable_checks, enable_checks, reset_format, set_format, set_mode
from .run_checks import _check_data
from .timer import print_time_elapsed, start_timer


@pd.api.extensions.register_series_accessor("check")
class SeriesVet:
    def __init__(self, pandas_obj: pd.Series) -> None:
        self._obj = pandas_obj

    def assert_data(
        self,
        condition: Union[str, Callable],
        pass_message: str = " ✔️ Assertion passed ",
        fail_message: str = " ㄨ Assertion failed ",
        raise_exception: bool = True,
        exception_to_raise: Type[BaseException] = DataError,
        verbose: bool = False,
    ) -> pd.Series:
        """Run DataFrameVet's method"""
        pd.DataFrame(self._obj).check.assert_data(
            condition=condition,
            subset=None,
            pass_message=pass_message,
            fail_message=fail_message,
            raise_exception=raise_exception,
            exception_to_raise=exception_to_raise,
            verbose=verbose,
        )
        return self._obj

    def describe(
        self,
        fn: Union[Callable, str] = lambda s: s,
        check_name: Union[str, None] = "📏 Distribution",
        **kwargs: Any,
    ) -> pd.Series:
        """Run DataFrameVet's method"""
        pd.DataFrame(self._obj).check.describe(
            fn=fn, check_name=check_name, subset=None, **kwargs
        )
        return self._obj

    def columns(
        self,
        fn: Union[Callable, str] = lambda s: s,
        check_name: Union[str, None] = "🏛️ Columns in series",
    ) -> pd.Series:
        """Run DataFrameVet's method"""
        pd.DataFrame(self._obj).check.columns(fn=fn, check_name=check_name, subset=None)
        return self._obj

    def disable_checks(self, enable_asserts: bool = True) -> pd.Series:
        disable_checks(enable_asserts)
        return self._obj

    def dtype(
        self,
        fn: Union[Callable, str] = lambda s: s,
        check_name: Union[str, None] = "🗂️ Data type",
    ) -> pd.Series:
        """Run DataFrameVet's method"""
        pd.DataFrame(self._obj).check.columns(fn=fn, check_name=check_name, subset=None)
        return self._obj

    def enable_checks(self, enable_asserts: bool = True) -> pd.Series:
        enable_checks(enable_asserts)
        return self._obj

    def function(
        self,
        fn: Union[Callable, str] = lambda s: s,
        check_name: Union[str, None] = None,
    ) -> pd.Series:
        pd.DataFrame(self._obj).check.function(
            fn=fn, check_name=check_name, subset=None
        )
        return self._obj

    def get_mode(self, check_name: Union[str, None] = "⚙️ PandasVet mode") -> pd.Series:
        pd.DataFrame(self._obj).check.get_mode(check_name=check_name)
        return self._obj

    def head(
        self,
        n: int = 5,
        fn: Union[Callable, str] = lambda s: s,
        check_name: Union[str, None] = None,
    ) -> pd.Series:
        """Run DataFrameVet's method"""
        pd.DataFrame(self._obj).check.head(
            n=n, fn=fn, check_name=check_name, subset=None
        )
        return self._obj

    def hist(
        self,
        fn: Union[Callable, str] = lambda s: s,
        check_name: Union[str, None] = None,
        **kwargs: Any,
    ) -> pd.Series:
        """Display a histogram. Only renders in IPython/Jupyter"""
        pd.DataFrame(self._obj).check.hist(
            fn=fn, check_name=check_name, subset=[], **kwargs
        )
        return self._obj

    def info(
        self,
        fn: Union[Callable, str] = lambda s: s,
        check_name: Union[str, None] = "ℹ️ Series info",
        **kwargs: Any,
    ) -> pd.Series:
        """Run DataFrameVet's method"""
        pd.DataFrame(self._obj).check.info(
            fn=fn, check_name=check_name, subset=None, **kwargs
        )
        return self._obj

    def memory_usage(
        self,
        fn: Union[Callable, str] = lambda s: s,
        check_name: Union[str, None] = "💾 Memory usage",
        **kwargs: Any,
    ) -> pd.Series:
        """Run DataFrameVet's method"""
        pd.DataFrame(self._obj).check.memory_usage(
            fn=fn, check_name=check_name, subset=None, **kwargs
        )
        return self._obj

    def ndups(
        self,
        fn: Union[Callable, str] = lambda s: s,
        check_name: Union[str, None] = None,
        **kwargs: Any,
    ) -> pd.Series:
        """Run DataFrameVet's method"""
        pd.DataFrame(self._obj).check.ndups(
            fn, check_name=check_name, subset=None, **kwargs
        )
        return self._obj

    def nnulls(
        self,
        fn: Union[Callable, str] = lambda s: s,
        by_column: bool = True,
        check_name: Union[str, None] = None,
    ) -> pd.Series:
        """Run DataFrameVet's method"""
        pd.DataFrame(self._obj).check.nnulls(
            fn=fn, by_column=by_column, check_name=check_name, subset=None
        )
        return self._obj

    def nrows(
        self,
        fn: Union[Callable, str] = lambda s: s,
        check_name: Union[str, None] = "☰ Rows",
    ) -> pd.Series:
        """Run DataFrameVet's method"""
        pd.DataFrame(self._obj).check.nrows(fn=fn, check_name=check_name, subset=None)
        return self._obj

    def nunique(
        self,
        fn: Union[Callable, str] = lambda s: s,
        check_name: Union[str, None] = None,
        **kwargs: Any,
    ) -> pd.Series:
        """"""
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
        fn: Union[Callable, str] = lambda s: s,
        check_name: Union[str, None] = "",
        **kwargs: Any,
    ) -> pd.Series:
        """Show Pandas plot. Only renders in IPython/Jupyter
        'title' kwarg overrides check_name as plot title"""
        pd.DataFrame(self._obj).check.plot(
            fn, check_name=check_name, subset=None, **kwargs
        )
        return self._obj

    def print(
        self,
        object: Any = None,  # Anything printable: str, int, list, DataFrame, etc
        fn: Union[Callable, str] = lambda s: s,
        check_name: Union[str, None] = None,
        max_rows: int = 10,
    ) -> pd.Series:
        """Run DataFrameVet's method"""
        pd.DataFrame(self._obj).check.print(
            object=object, fn=fn, check_name=check_name, max_rows=max_rows, subset=None
        )
        return self._obj

    def print_time_elapsed(
        self, check_name: Union[str, None] = "Time elapsed", units: str = "auto"
    ) -> pd.Series:
        print_time_elapsed(
            check_name=check_name, units=units
        )  # Call the public function
        return self._obj

    def reset_format(self) -> pd.Series:
        """Re-initilaize all Pandas Vet options for formatting"""
        reset_format()
        return self._obj

    def set_format(self, **kwargs: Any) -> pd.Series:
        set_format(**kwargs)
        return self._obj

    def set_mode(self, enable_checks: bool, enable_asserts: bool) -> pd.Series:
        set_mode(enable_checks, enable_asserts)
        return self._obj

    def shape(
        self,
        fn: Union[Callable, str] = lambda s: s,
        check_name: Union[str, None] = "📐 Shape",
    ) -> pd.Series:
        """Run DataFrameVet's method"""
        pd.DataFrame(self._obj).check.shape(fn=fn, check_name=check_name, subset=None)
        return self._obj

    def start_timer(self, verbose: bool = False) -> pd.Series:
        start_timer(verbose)  # Call the public function
        return self._obj

    def tail(
        self,
        n: int = 5,
        fn: Union[Callable, str] = lambda s: s,
        check_name: Union[str, None] = None,
    ) -> pd.Series:
        """Run DataFrameVet's method"""
        pd.DataFrame(self._obj).check.tail(
            n=n, fn=fn, check_name=check_name, subset=None
        )
        return self._obj

    def unique(
        self,
        fn: Union[Callable, str] = lambda s: s,
        check_name: Union[str, None] = None,
    ) -> pd.Series:
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
        max_rows: int = 10,
        fn: Union[Callable, str] = lambda s: s,
        check_name: Union[str, None] = None,
        **kwargs: Any,
    ) -> pd.Series:
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
        fn: Union[Callable, str] = lambda s: s,
        verbose: bool = False,
        **kwargs: Any,
    ) -> pd.Series:
        """Run DataFrameVet's method"""
        (
            pd.DataFrame(self._obj).check.write(
                path=path, format=format, fn=fn, subset=None, verbose=verbose, **kwargs
            )
        )
        return self._obj
