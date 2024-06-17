"""Dataframe methods to test in batch"""

import pandas_vet as pdv


def method_assert_data():
    return lambda df, args: df.check.assert_data(
        condition=lambda s: s.sum() > 0,  # Series because we apply subset first
        subset=args["first_num_col"],
        pass_message="Pass",
        fail_message="Fail",
        raise_exception=False,
        exception_to_raise=AttributeError,
        verbose=True,
    )


def method_columns():
    return lambda df, _: df.check.columns(fn=lambda df: df.dropna(), check_name="Test")


def method_describe():
    return lambda df, _: df.check.describe(fn=lambda df: df.dropna(), check_name="Test")


def method_disable_checks():
    return lambda df, _: df.check.disable_checks()


def method_dtypes():
    return lambda df, _: df.check.dtypes(fn=lambda df: df.dropna(), check_name="Test")


def method_enable_checks():
    return lambda df, _: df.check.enable_checks()


def method_function():
    return lambda df, _: df.check.function(
        lambda df: df.assign(new_col=4), check_name="Test"
    )


def method_get_mode():
    return lambda df, _: df.check.get_mode(check_name="Test")


def method_head():
    return lambda df, _: df.check.head(
        n=10, fn=lambda df: df.dropna(), check_name="Test"
    )


def method_hist():
    return lambda df, _: df.check.hist(
        fn=lambda df: df.dropna(), check_name="Test", grid=False, bins=100, legend=True
    )


def method_info():
    return lambda df, _: df.check.info(
        fn=lambda df: df.dropna(),
        check_name="Test",
        verbose=True,
        max_cols=1,
        show_counts=False,
    )


def method_memory_usage():
    return lambda df, _: df.check.memory_usage(
        fn=lambda df: df.dropna(), check_name="Test", index=False, deep=True
    )


def method_ncols():
    return lambda df, _: df.check.ncols(fn=lambda df: df.dropna(), check_name="Test")


def method_ndups():
    return lambda df, _: df.check.ndups(
        fn=lambda df: df.dropna(), check_name="Test", keep=False
    )


def method_nnulls():
    return lambda df, _: df.check.nnulls(
        fn=lambda df: df.dropna(), by_column=False, check_name="Test"
    )


def method_nrows():
    return lambda df, _: df.check.nrows(fn=lambda df: df.dropna(), check_name="Test")


def method_nunique():
    return lambda df, args: df.check.nunique(
        column=args["first_num_col"],
        fn=lambda df: df.dropna(),
        check_name="Test",
        dropna=False,
    )


def method_plot():
    return lambda df, _: df.check.plot(
        fn=lambda df: df.dropna(),
        check_name="Test",
        subplots=True,
        title="Override",
    )


def method_print():
    return lambda df, _: df.check.print(fn=lambda df: df.dropna(), check_name="Test")


def method_print_time_elapsed():
    return lambda df, _: df.check.print_time_elapsed(
        start_time=pdv.start_timer(), lead_in="Test", units="hours"
    )


def method_reset_format():
    return lambda df, _: df.check.reset_format()


def method_set_format():
    return lambda df, _: df.check.set_format(use_emojis=False)


def method_set_mode():
    return lambda df, _: df.check.set_mode(enable_checks=False, enable_asserts=False)


def method_shape():
    return lambda df, _: df.check.shape(fn=lambda df: df.dropna(), check_name="Test")


def method_tail():
    return lambda df, _: df.check.tail(
        n=20, fn=lambda df: df.dropna(), check_name="Test"
    )


def method_unique():
    return lambda df, args: df.check.unique(
        column=args["first_num_col"], fn=lambda df: df.dropna(), check_name="Test"
    )


def method_value_counts():
    return lambda df, args: df.check.value_counts(
        column=args["first_num_col"],
        max_rows=3,
        fn=lambda df: df.dropna(),
        check_name="Test",
        dropna=False,
        normalize=True,
    )


def method_write():
    return lambda df, args: df.check.write(
        path=f'{args["tmp_path"]}/test.csv', fn=lambda df: df.dropna(), index=False
    )
