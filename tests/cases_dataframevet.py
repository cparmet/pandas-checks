"""Assets used for test_dataframevet.py"""
# --------------------
# DF methods to test
# --------------------
def method_assert_data():
    return lambda df, args: df.check.assert_data(
        lambda df: df[args["first_num_col"]].sum() > 0
    )


def method_columns():
    return lambda df, _: df.check.columns()


def method_describe():
    return lambda df, _: df.check.describe()


def method_disable_checks():
    return lambda df, _: df.check.disable_checks()


def method_dtypes():
    return lambda df, _: df.check.dtypes()


def method_enable_checks():
    return lambda df, _: df.check.enable_checks()


def method_function():
    return lambda df, _: df.check.function(lambda df: df.assign(new_col=4))


def method_get_mode():
    return lambda df, _: df.check.get_mode()


def method_head():
    return lambda df, _: df.check.head()


def method_hist():
    return lambda df, _: df.check.hist()


def method_info():
    return lambda df, _: df.check.info()


def method_memory_usage():
    return lambda df, _: df.check.memory_usage()


def method_ncols():
    return lambda df, _: df.check.ncols()


def method_ndups():
    return lambda df, _: df.check.ndups()


def method_nnulls():
    return lambda df, _: df.check.nnulls()


def method_nrows():
    return lambda df, _: df.check.nrows()


def method_nunique():
    return lambda df, args: df.check.nunique(args["first_num_col"])


def method_plot():
    return lambda df, _: df.check.plot()


def method_print():
    return lambda df, _: df.check.print()


def method_print_time_elapsed():
    return lambda df, _: df.check.start_timer().check.print_time_elapsed()


def method_reset_format():
    return lambda df, _: df.check.reset_format()


def method_set_format():
    return lambda df, _: df.check.set_format(use_emojis=False)


def method_set_mode():
    return lambda df, _: df.check.set_mode(enable_checks=False, enable_asserts=False)


def method_shape():
    return lambda df, _: df.check.shape()


def method_start_timer():
    return lambda df, _: df.check.start_timer()


def method_tail():
    return lambda df, _: df.check.tail()


def method_unique():
    return lambda df, args: df.check.unique(column=args["first_num_col"])


def method_value_counts():
    return lambda df, args: df.check.value_counts(column=args["first_num_col"])


def method_write():
    return lambda df, args: df.check.write(f'{args["tmp_path"]}/test.csv')
