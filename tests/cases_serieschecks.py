"""SeriesCheck methods to test in batch
that they don't change the actual series
in the method chain """

import pandas_checks as pdc

## These methods return:
# 1. A lambda function to run the test
# 2. True if the method only runs on numeric columns, False if it runs on any dtype.
#    Which tells test_serieschecks.py whether it can test this method on a str column, for example.


def method_assert_data():
    return (
        lambda s, _: s.check.assert_data(
            lambda s: s.shape[0] > 0,
            raise_exception=False,
        ),
        False,
    )


def method_assert_datetime():
    return (
        lambda s, _: s.check.assert_datetime(
            raise_exception=False,
        ),
        False,
    )


def method_assert_float():
    return (
        lambda s, _: s.check.assert_float(
            raise_exception=False,
        ),
        False,
    )


def method_assert_int():
    return (
        lambda s, _: s.check.assert_int(
            raise_exception=False,
        ),
        False,
    )


def method_assert_less_than():
    return (
        lambda s, _: s.check.assert_less_than(
            max=1000,
            raise_exception=False,
        ),
        True,
    )


def method_assert_greater_than():
    return (
        lambda s, _: s.check.assert_greater_than(
            min=-1000,
            raise_exception=False,
        ),
        True,
    )


def method_assert_negative():
    return (
        lambda s, _: s.check.assert_negative(
            raise_exception=False,
        ),
        True,
    )


def method_assert_no_nulls():
    return (
        lambda s, _: s.check.assert_no_nulls(
            raise_exception=False,
        ),
        False,
    )


def method_assert_null():
    return (
        lambda s, _: s.check.assert_null(
            raise_exception=False,
        ),
        False,
    )


def method_assert_positive():
    return (
        lambda s, _: s.check.assert_positive(
            raise_exception=False,
        ),
        True,
    )


def method_assert_str():
    return (
        lambda s, _: s.check.assert_str(
            raise_exception=False,
        ),
        False,
    )


def method_assert_timedelta():
    return (
        lambda s, _: s.check.assert_timedelta(
            raise_exception=False,
        ),
        False,
    )


def method_assert_type():
    return (
        lambda s, _: s.check.assert_type(
            dtype=float,
            raise_exception=False,
        ),
        False,
    )


def method_assert_unique():
    return (
        lambda s, _: s.check.assert_unique(
            raise_exception=False,
        ),
        False,
    )


def method_describe():
    return (
        lambda s, _: s.check.describe(fn=lambda s: s.dropna(), check_name="Test"),
        False,
    )


def method_disable_checks():
    return lambda s, _: s.check.disable_checks(), False


def method_dtype():
    return lambda s, _: s.check.dtype(fn=lambda s: s.dropna(), check_name="Test"), False


def method_enable_checks():
    return lambda s, _: s.check.enable_checks(), False


def method_function():
    return (
        lambda s, _: s.check.function(lambda s: s.shape[0] * 2, check_name="Test"),
        False,
    )


def method_get_mode():
    return lambda s, _: s.check.get_mode(check_name="Test"), False


def method_head():
    return (
        lambda s, _: s.check.head(n=7, fn=lambda s: s.dropna(), check_name="Test"),
        False,
    )


def method_hist():
    return (
        lambda s, _: s.check.hist(
            fn=lambda s: s.dropna(), check_name="Test", grid=True, bins=5, legend=False
        ),
        False,
    )


def method_info():
    return (
        lambda s, _: s.check.info(
            fn=lambda s: s.dropna(),
            check_name="Test",
            verbose=True,
            show_counts=True,
        ),
        False,
    )


def method_memory_usage():
    return (
        lambda s, _: s.check.memory_usage(
            fn=lambda s: s.dropna(), check_name="Test", index=True, deep=True
        ),
        False,
    )


def method_ndups():
    return (
        lambda s, _: s.check.ndups(
            fn=lambda s: s.dropna(), check_name="Test", keep="last"
        ),
        False,
    )


def method_nnulls():
    return (
        lambda s, _: s.check.nnulls(fn=lambda s: s.dropna(), check_name="Test"),
        False,
    )


def method_nrows():
    return lambda s, _: s.check.nrows(fn=lambda s: s.dropna(), check_name="Test"), False


def method_nunique():
    return (
        lambda s, _: s.check.nunique(
            fn=lambda s: s.dropna(), check_name="Test", dropna=False
        ),
        False,
    )


def method_plot():
    return (
        lambda s, _: s.check.plot(
            fn=lambda s: s.dropna(),
            check_name="Test",
            title="Override",
        ),
        False,
    )


def method_print():
    return lambda s, _: s.check.print(fn=lambda s: s.dropna(), check_name="Test"), False


def method_print_time_elapsed():
    return (
        lambda s, _: s.check.print_time_elapsed(
            pdc.start_timer(), lead_in="Test", units="minutes"
        ),
        False,
    )


def method_reset_format():
    return lambda s, _: s.check.reset_format(), False


def method_set_format():
    return lambda s, _: s.check.set_format(use_emojis=False), False


def method_set_mode():
    return (
        lambda s, _: s.check.set_mode(enable_checks=False, enable_asserts=False),
        False,
    )


def method_shape():
    return lambda s, _: s.check.shape(fn=lambda s: s.dropna(), check_name="Test"), False


def method_tail():
    return lambda s, _: s.check.tail(fn=lambda s: s.dropna(), check_name="Test"), False


def method_unique():
    return (
        lambda s, _: s.check.unique(fn=lambda s: s.dropna(), check_name="Test"),
        False,
    )


def method_value_counts():
    return (
        lambda s, _: s.check.value_counts(
            fn=lambda s: s.dropna(), check_name="Test", dropna=False, normalize=True
        ),
        False,
    )


def method_write():
    return (
        lambda s, args: s.check.write(f'{args["tmp_path"]}/test.csv', index=False),
        False,
    )
