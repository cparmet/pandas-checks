from .display import reset_format, set_format
from .run_checks import _check_data
from .timer import print_time_elapsed, start_timer
import matplotlib.pyplot as plt
import pandas as pd
from pandas.core.groupby.groupby import DataError

@pd.api.extensions.register_series_accessor("check")
class SeriesVet:
    # Where possible we point to DataFrameVet, setting subset=None"""
    def __init__(self, pandas_obj):
        self._obj = pandas_obj
    
    def set_format(self, **kwargs):
        set_format(**kwargs)
        return self._obj

    def reset_format(self):
        """Re-initilaize all Pandas Vet options for formatting"""
        reset_format()
        return self._obj

    def assert_data(
            self,
            condition,
            pass_message=" ✔️ Assertion passed ",
            fail_message=" ㄨ Assertion failed ",
            raise_exception=True,
            exception_to_raise=DataError,
            verbose=False
            ):
        """Run DataFrameVet's method"""
        pd.DataFrame(self._obj).check.assert_data(
            condition=condition,
            subset=None,
            pass_message=pass_message,
            fail_message=fail_message,
            raise_exception=raise_exception,
            exception_to_raise=exception_to_raise,
            verbose=verbose
            )
        return self._obj

    def describe(self, fn=lambda s: s, check_name='📏 Distribution',**kwargs):
        """Run DataFrameVet's method"""
        pd.DataFrame(self._obj).check.describe(fn=fn, check_name=check_name, subset=None, **kwargs)
        return self._obj

    def columns(self, fn=lambda s: s, check_name='🏛️ Columns in series'):
        """Run DataFrameVet's method"""
        pd.DataFrame(self._obj).check.columns(fn=fn, check_name=check_name, subset=None)
        return self._obj
    
    def dtype(self, fn=lambda s: s, check_name='🗂️ Data type'):
        """Run DataFrameVet's method"""
        pd.DataFrame(self._obj).check.columns(fn=fn, check_name=check_name, subset=None)
        return self._obj

    def evaluate(self, fn=lambda s: s, check_name=None):
        pd.DataFrame(self._obj).check.evaluate(fn=fn, check_name=check_name, subset=None)
        return self._obj

    def head(self, n=5, fn=lambda s: s, check_name=None):
        """Run DataFrameVet's method"""
        pd.DataFrame(self._obj).check.head(n=n, fn=fn, check_name=check_name, subset=None)
        return self._obj

    def hist(self, fn=lambda s: s, check_name=None, **kwargs):
        """Display a histogram. Only renders in IPython/Jupyter"""
        pd.DataFrame(self._obj).check.hist(fn=fn, check_name=check_name, subset=[], **kwargs)
        return self._obj

    def info(self, fn=lambda s: s, check_name='ℹ️ Series info', **kwargs):
        """Run DataFrameVet's method"""
        pd.DataFrame(self._obj).check.info(fn=fn, check_name=check_name, subset=None, **kwargs)
        return self._obj

    def memory_usage(self, fn=lambda df:df, check_name='💾 Memory usage', **kwargs):
        """Run DataFrameVet's method"""
        pd.DataFrame(self._obj).check.memory_usage(fn=fn, check_name=check_name, subset=None, **kwargs)
        return self._obj

    def ndups(self, fn=lambda s: s, check_name=None, **kwargs):
        """Run DataFrameVet's method"""
        pd.DataFrame(self._obj).check.ndups(fn, check_name=check_name, subset=None, **kwargs)
        return self._obj

    def nnulls(self, fn=lambda s: s, by_column=True, check_name=None):
        """Run DataFrameVet's method"""
        pd.DataFrame(self._obj).check.nnulls(fn=fn, by_column=by_column, check_name=check_name, subset=None)
        return self._obj

    def nrows(self, fn=lambda s: s, check_name='☰ Rows'):
        """Run DataFrameVet's method"""
        pd.DataFrame(self._obj).check.nrows(fn=fn, check_name=check_name, subset=None)
        return self._obj

    def nunique(self, fn=lambda s: s, check_name=None, **kwargs):
        """"""
        _check_data(
           self._obj,
            check_fn=lambda s: s.nunique(**kwargs),
            modify_fn=fn,
            check_name=check_name if check_name else f"🌟 Unique values in {self._obj.name if self._obj.name else 'series'}"
            )
        return self._obj

    def plot(self, fn=lambda s: s, check_name="", **kwargs):
        """Show Pandas plot. Only renders in IPython/Jupyter
        'title' kwarg overrides check_name as plot title"""
        pd.DataFrame(self._obj).check.plot(fn, check_name=check_name, subset=None, **kwargs)
        return self._obj

    def print(self, text=None, fn=lambda s: s, check_name=None, max_rows=10):
        """Run DataFrameVet's method"""
        pd.DataFrame(self._obj).check.print(text=text, fn=fn, check_name=check_name, max_rows=max_rows, subset=None)
        return self._obj

    def shape(self, fn=lambda s: s, check_name='📐 Shape'):
        """Run DataFrameVet's method"""
        pd.DataFrame(self._obj).check.shape(fn=fn, check_name=check_name, subset=None)
        return self._obj

    def start_timer(self, verbose=False):
        start_timer(verbose) # Call the public function
        return self._obj

    def tail(self, n=5, fn=lambda s: s, check_name=None):
        """Run DataFrameVet's method"""
        pd.DataFrame(self._obj).check.tail(n=n, fn=fn, check_name=check_name, subset=None)
        return self._obj
    
    def print_time_elapsed(self, check_name="Time elapsed", units="auto"):
        print_time_elapsed(check_name=check_name, units=units) # Call the public function
        return self._obj

    def unique(self, fn=lambda s: s, check_name=None):
        _check_data(
            self._obj,
            check_fn=lambda s: s.unique().tolist(),
            modify_fn=fn,
            check_name=check_name if check_name else f"🌟 Unique values of {self._obj.name if self._obj.name else 'series'}"
            )
        return self._obj

    def value_counts(self, max_rows=10, fn=lambda s: s, check_name=None, **kwargs):
        _check_data(
            self._obj,
            check_fn=lambda s: s.value_counts(**kwargs).head(max_rows),
            modify_fn=fn,
            check_name=check_name if check_name else f"🧮 Value counts, first {max_rows} values" if max_rows else f"🧮 Value counts"
            )
        return self._obj

    def write(self, path, format=None, fn=lambda s: s, verbose=False, **kwargs):
        """Run DataFrameVet's method"""
        (
            pd.DataFrame(self._obj)
            .check.write(
                path=path,
                format=format,
                fn=fn,
                subset=None,
                verbose=verbose,
                **kwargs
            )
        )
        return self._obj