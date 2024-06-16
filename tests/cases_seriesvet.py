"""Assets used for test_seriesvet.py"""
import pandas as pd


# --------------------
# S methods to test
# --------------------
def method_assert_data():
    return lambda s, _: s.check.assert_data(lambda s: s.shape[0] > 0)


def method_describe():
    return lambda s, _: s.check.describe()


def method_disable_checks():
    return lambda s, _: s.check.disable_checks()


def method_dtype():
    return lambda s, _: s.check.dtype()


def method_enable_checks():
    return lambda s, _: s.check.enable_checks()


def method_function():
    return lambda s, _: s.check.function(lambda s: s.shape[0] * 2)


def method_get_mode():
    return lambda s, _: s.check.get_mode()


def method_head():
    return lambda s, _: s.check.head()


def method_hist():
    return lambda s, _: s.check.hist()


def method_info():
    return lambda s, _: s.check.info()


def method_memory_usage():
    return lambda s, _: s.check.memory_usage()


def method_ndups():
    return lambda s, _: s.check.ndups()


def method_nnulls():
    return lambda s, _: s.check.nnulls()


def method_nrows():
    return lambda s, _: s.check.nrows()


def method_nunique():
    return lambda s, _: s.check.nunique()


def method_plot():
    return lambda s, _: s.check.plot()


def method_print():
    return lambda s, _: s.check.print()


def method_print_time_elapsed():
    return lambda s, _: s.check.start_timer().check.print_time_elapsed()


def method_reset_format():
    return lambda s, _: s.check.reset_format()


def method_set_format():
    return lambda s, _: s.check.set_format(use_emojis=False)


def method_set_mode():
    return lambda s, _: s.check.set_mode(enable_checks=False, enable_asserts=False)


def method_shape():
    return lambda s, _: s.check.shape()


def method_start_timer():
    return lambda s, _: s.check.start_timer()


def method_tail():
    return lambda s, _: s.check.tail()


def method_unique():
    return lambda s, _: s.check.unique()


def method_value_counts():
    return lambda s, _: s.check.value_counts()


def method_write():
    return lambda s, args: s.check.write(f'{args["tmp_path"]}/test.csv')
