from .display import (
    _display_line,
    _display_plot,
    _display_plot_title,
    _display_table_title,
    reset_format,
    set_format
)
from .options import _initialize_format_options
from .run_checks import _check_data, _modify_data
from .timer import print_time_elapsed, start_timer
from .utils import _lambda_to_string

import matplotlib.pyplot as plt
import pandas as pd
from pandas.core.groupby.groupby import DataError


## Public methods added to Pandas DataFrame
@pd.api.extensions.register_dataframe_accessor("check")
class DataFrameVet:
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
            subset=None,
            pass_message=" ✔️ Assertion passed ",
            fail_message=" ㄨ Assertion failed ",
            raise_exception=True,
            exception_to_raise=DataError,
            verbose=False
            ):
        """Test whether dataframe meets condition, optionally raise an exception if not.

        condition: can be a lambda function or an evaluable string referring to `df`, such as "df.shape[0]>10"
        """
        data = self._obj[subset] if subset else self._obj
        if callable(condition):
            result = condition(data)
            condition_str = _lambda_to_string(condition)
        elif isinstance(condition, str):
            result = eval(condition_str:=condition, {}, {"df": data})
        else:
            raise TypeError(f"Argument `condition` is of unexpected type {type(condition)}")
        if not result:
            if raise_exception:
                raise exception_to_raise(f"{fail_message}: {condition_str}")
            else:
                _display_line(
                    lead_in=fail_message,
                    line=condition_str,
                    colors={
                        "lead_in_text_color":pd.get_option("vet.fail_text_fg_color"),
                        "lead_in_background_color":pd.get_option("vet.fail_text_bg_color")
                        }
                    )
        if verbose:
            _display_line(
                lead_in=pass_message,
                line=condition_str,
                colors={
                    "lead_in_text_color":pd.get_option("vet.success_text_fg_color"),
                    "lead_in_background_color":pd.get_option("vet.success_text_bg_color")
                }
            )
        return self._obj

    def describe(self, fn=lambda df: df, subset=None, check_name='📏 Distributions',**kwargs):
        _check_data(
            self._obj,
            check_fn=lambda df: df.describe(**kwargs),
            modify_fn=fn,
            subset=subset,
            check_name=check_name
            )
        return self._obj

    def columns(self, fn=lambda df: df, subset=None, check_name='🏛️ Columns'):
        _check_data(
            self._obj,
            check_fn=lambda df: df.columns.tolist(),
            modify_fn=fn,
            subset=subset,
            check_name=check_name
            )
        return self._obj

    def dtypes(self, fn=lambda df: df, subset=None, check_name='🗂️ Data types'):
        _check_data(
            self._obj,
            check_fn=lambda df: df.dtypes,
            modify_fn=fn,
            subset=subset,
            check_name=check_name
            )
        return self._obj

    def evaluate(self, fn=lambda df: df, subset=None, check_name=None):
        """Run an arbitrary operation on a DataFrame and show the result.

        fn: Can be a lambda function or an evaluable string referring to `df`, such as "df.shape[0]>10"
        """
        _check_data(
            self._obj,
            modify_fn=fn,
            subset=subset,
            check_name=check_name)
        return self._obj
    
    def head(self, n=5, fn=lambda df: df, subset=None, check_name=None):
        _check_data(
            self._obj,
            check_fn=lambda df: df.head(n),
            modify_fn=fn,
            subset=subset,
            check_name=check_name if check_name else f"⬆️ First {n} rows"
            )
        return self._obj

    def hist(self, fn=lambda df: df, subset=[], check_name=None, **kwargs):
        """Display a histogram. Only renders in IPython/Jupyter"""
        if not pd.core.config_init.is_terminal(): # Only display if in IPython/Jupyter, or we'd just print the title
            _display_plot_title(
                    check_name if check_name else "📏 Distribution" if len(subset)==1 else "Distributions"
                )
            fig, ax = plt.subplots()
            _ = (
                _modify_data(self._obj, fn, subset)
                .hist(ax=ax, **kwargs)
                )
            _display_plot(fig)
        return self._obj

    def info(self, fn=lambda df: df, subset=None, check_name='ℹ️ Info', **kwargs):
        """Don't use display or check_name comes below report """
        _display_table_title(check_name)
        (
            _modify_data(self._obj, fn, subset)
            .info(**kwargs)
        )
        return self._obj
    
    def memory_usage(self, fn=lambda df: df, subset=None, check_name='💾 Memory usage', **kwargs):
        _check_data(
            self._obj,
            check_fn=lambda df: df.memory_usage(**kwargs),
            modify_fn=fn,
            subset=subset,
            check_name=check_name
            )
        return self._obj
        
    def ncols(self, fn=lambda df: df, subset=None, check_name='🏛️ Columns'):
        _check_data(
            self._obj,
            check_fn=lambda df: df.shape[1],
            modify_fn=fn,
            subset=subset,
            check_name=check_name
            )
        return self._obj

    def ndups(self, fn=lambda df: df, subset=None, check_name=None, **kwargs):
        """kwargs are arguments to .duplicated() """
        _check_data(
            self._obj,
            check_fn=lambda df: df.duplicated(**kwargs).sum(),
            modify_fn=fn,
            subset=subset,
            check_name=check_name if check_name else f'👯‍♂️ Rows with duplication in {subset}' if subset else '👯‍♂️ Duplicated rows')
        return self._obj

    def nnulls(self, fn=lambda df: df, subset=None, by_column=True, check_name=None):
        """

        by_column = False to count rows that have any NaNs in any columns
        """
        data = _modify_data(self._obj, fn, subset)
        na_counts = data.isna().any(axis=1).sum() if isinstance(data, pd.DataFrame) and not by_column else data.isna().sum()
        if not check_name:
            if isinstance(na_counts, (pd.DataFrame, pd.Series)): # Report result as a pandas object
                _check_data(na_counts, check_name=f'👻 Rows with NaNs in {subset}' if subset else '👻 Rows with NaNs')
            else: # Report on one line
                _display_line(
                    (f'👻 Rows with NaNs in {subset}: ' if subset else '👻 Rows with NaNs: ')
                    + f"{na_counts} out of {data.shape[0]}" 
                )  
        else:
            _display_line(f"{check_name}: {na_counts}")
        return self._obj

    def nrows(self, fn=lambda df: df, subset=None, check_name='☰ Rows'):
        _check_data(
            self._obj,
            check_fn=lambda df: df.shape[0],
            modify_fn=fn,
            subset=subset,
            check_name=check_name
            )
        return self._obj

    def nunique(self, column, fn=lambda df: df, check_name=None, **kwargs):
        """Run SeriesVet method.

        Note that `fn` is applied to the dataframe _before_ filtering columns to `column`.

        If you want to apply `fn` _after_ filtering to column, set `column=None`
        and start `fn` with a column selection, i.e. `fn=lambda df: df["my_column"].stuff()`
        """
        (
            _modify_data(self._obj, fn=fn, subset=column) # Apply fn, then filter to `column`
            .check.nunique( # Use SeriesVet method
                fn=lambda df: df, # Identity function
                check_name=check_name,
                **kwargs
            )
        )
        return self._obj

    def plot(self, fn=lambda df: df, subset=None, check_name="", **kwargs):
        """Show Pandas plot. Only renders in IPython/Jupyter
        'title' kwarg overrides check_name as plot title"""
        if not pd.core.config_init.is_terminal(): # Only display if in IPython/Jupyter, or we'd just print the title
            _display_plot_title(check_name if "title" not in kwargs else kwargs["title"])
            fig, ax = plt.subplots()
            _ = (
                _modify_data(self._obj, fn, subset)
                .plot(ax=ax, **kwargs)
            )
            _display_plot(fig)
        return self._obj
    
    def print(self, text=None, fn=lambda df: df, subset=None, check_name=None, max_rows=10):
        _check_data(
            text if text else self._obj,
            check_fn=lambda data: data if text else data.head(max_rows),
            modify_fn=fn,
            subset=subset,
            check_name=check_name
            )
        return self._obj
    
    def shape(self, fn=lambda df: df, subset=None, check_name='📐 Shape'):
        """See nrows, ncols"""
        _check_data(
            self._obj,
            check_fn=lambda df: df.shape,
            modify_fn=fn,
            subset=subset,
            check_name=check_name
            )
        return self._obj

    def start_timer(self, verbose=False):
        start_timer(verbose) # Call the public function
        return self._obj

    def tail(self, n=5, fn=lambda df: df, subset=None, check_name=None):            
        _check_data(
            self._obj,
            check_fn=lambda df: df.tail(n),
            modify_fn=fn,
            subset=subset,
            check_name=check_name if check_name else f"⬇️ Last {n} rows"
            )
        return self._obj
    
    def print_time_elapsed(self, check_name="Time elapsed", units="auto"):
        print_time_elapsed(check_name=check_name, units=units) # Call the public function
        return self._obj

    def unique(self, column, fn=lambda df: df, check_name=None):
        """Run SeriesVet's method

        Note that `fn` is applied to the dataframe _before_ filtering columns to `column`.

        If you want to apply `fn` _after_ filtering to column, set `column=None`
        and start `fn` with a column selection, i.e. `fn=lambda df: df["my_column"].stuff()`
        """
        (
            _modify_data(self._obj, fn=fn, subset=column) # Apply fn, then filter to `column`
            .check.unique( # Use SeriesVet method
                fn=lambda df: df, # Identify function
                check_name=check_name,
                )
        )
        return self._obj

    def value_counts(self, column, max_rows=10, fn=lambda df: df, check_name=None, **kwargs):
        """Run SeriesVet's method
        
        Note that `fn` is applied to the dataframe _before_ filtering columns to `column`.
        
        If you want to apply `fn` _after_ filtering to column, set `column=None` 
        and start `fn` with a column selection, i.e. `fn=lambda df: df["my_column"].stuff()`

        """
        (
            _modify_data(self._obj, fn=fn, subset=column) # Apply fn, then filter to `column``
            .check.value_counts( # Use SeriesVet method
                max_rows=max_rows,
                fn=lambda df: df, # Identity function
                check_name=check_name,
                **kwargs
            )
        )
        return self._obj

    def write(self, path, format=None, fn=lambda df: df, subset=None, verbose=False, **kwargs):
        """File format is inferred from path extension (.csv). Or pass `format` to force
        Kwargs are passed to to_excel/to_csv/to_parquet"""
        format_clean = format.lower().replace(".", "").strip() if format else None
        data = _modify_data(self._obj, fn, subset)
        if path.endswith(".xls") or path.endswith(".xlsx") or format_clean in ["xlsx", "xls", "excel"]:
            data.to_excel(path, **kwargs)
        elif path.endswith(".csv") or format_clean == "csv":
            data.to_csv(path, **kwargs)
        elif path.endswith(".tsv") or format_clean == "tsv":
            data.to_csv(path, sep="\t", **kwargs)
        elif path.endswith(".parquet") or format_clean == "parquet":
            data.to_parquet(path, **kwargs)
        else:
            raise AttributeError(f"Can't write data to file. Unknown file extension in: {path}. ")
        if verbose:
            _display_line("📦 Wrote file {path}")
        return self._obj


# Initialize configuration
_initialize_format_options()