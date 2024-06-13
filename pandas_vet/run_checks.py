from .display import _display_check
from .options import get_mode


def _modify_data(data, fn=lambda df: df, subset=None):
    """Apply user's arbitrary modifications to a data object then subset the columns if requested.

    If all arguments are defaults, this function returns `data` unchanged.

    `data` may a Pandas DataFrame, Series, string, or other variable

    fn may be a lambda function or a string describing an operation that can be performed with 'eval()'

    """
    if callable(fn):
        data = fn(data)
    elif isinstance(fn, str):
        data = eval(fn, {}, {"df": data})
    else:
        raise TypeError(f"Argument `fn` is of unexpected type {type(fn)}")
    return data[subset] if subset else data


def _check_data(
    data,
    check_fn=lambda df: df,
    modify_fn=lambda df: df,
    subset=None,
    check_name=None,
    **kwargs,
):
    if not get_mode()["enable_checks"]:
        return None
    return _display_check(  # 3. Report the result
        check_fn(  # 2. After applying the method's operation to the data, like value_counts() or dtypes. May return a DF, an int, etc
            _modify_data(
                data, fn=modify_fn, subset=subset
            )  # 1. After first applying user's modifications to the data before checking it
        ),
        name=check_name if check_name else subset,
    )
