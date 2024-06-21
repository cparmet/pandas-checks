"""Series methods to test in batch"""

import pandas_checks as pdc


def method_assert_data():
    return lambda s, _: s.check.assert_data(
        lambda s: s.shape[0] > 0,
        pass_message="Pass",
        fail_message="Fail",
        raise_exception=False,
        exception_to_raise=AttributeError,
        verbose=True,
    )


def method_describe():
    return lambda s, _: s.check.describe(fn=lambda s: s.dropna(), check_name="Test")


def method_disable_checks():
    return lambda s, _: s.check.disable_checks()


def method_dtype():
    return lambda s, _: s.check.dtype(fn=lambda s: s.dropna(), check_name="Test")


def method_enable_checks():
    return lambda s, _: s.check.enable_checks()


def method_function():
    return lambda s, _: s.check.function(lambda s: s.shape[0] * 2, check_name="Test")


def method_get_mode():
    return lambda s, _: s.check.get_mode(check_name="Test")


def method_head():
    return lambda s, _: s.check.head(n=7, fn=lambda s: s.dropna(), check_name="Test")


def method_hist():
    return lambda s, _: s.check.hist(
        fn=lambda s: s.dropna(), check_name="Test", grid=True, bins=5, legend=False
    )


def method_info():
    return lambda s, _: s.check.info(
        fn=lambda s: s.dropna(),
        check_name="Test",
        verbose=True,
        show_counts=True,
    )


def method_memory_usage():
    return lambda s, _: s.check.memory_usage(
        fn=lambda s: s.dropna(), check_name="Test", index=True, deep=True
    )


def method_ndups():
    return lambda s, _: s.check.ndups(
        fn=lambda s: s.dropna(), check_name="Test", keep="last"
    )


def method_nnulls():
    return lambda s, _: s.check.nnulls(fn=lambda s: s.dropna(), check_name="Test")


def method_nrows():
    return lambda s, _: s.check.nrows(fn=lambda s: s.dropna(), check_name="Test")


def method_nunique():
    return lambda s, _: s.check.nunique(
        fn=lambda s: s.dropna(), check_name="Test", dropna=False
    )


def method_plot():
    return lambda s, _: s.check.plot(
        fn=lambda s: s.dropna(),
        check_name="Test",
        title="Override",
    )


def method_print():
    return lambda s, _: s.check.print(fn=lambda s: s.dropna(), check_name="Test")


def method_print_time_elapsed():
    return lambda s, _: s.check.print_time_elapsed(
        pdc.start_timer(), lead_in="Test", units="minutes"
    )


def method_reset_format():
    return lambda s, _: s.check.reset_format()


def method_set_format():
    return lambda s, _: s.check.set_format(use_emojis=False)


def method_set_mode():
    return lambda s, _: s.check.set_mode(enable_checks=False, enable_asserts=False)


def method_shape():
    return lambda s, _: s.check.shape(fn=lambda s: s.dropna(), check_name="Test")


def method_tail():
    return lambda s, _: s.check.tail(fn=lambda s: s.dropna(), check_name="Test")


def method_unique():
    return lambda s, _: s.check.unique(fn=lambda s: s.dropna(), check_name="Test")


def method_value_counts():
    return lambda s, _: s.check.value_counts(
        fn=lambda s: s.dropna(), check_name="Test", dropna=False, normalize=True
    )


def method_write():
    return lambda s, args: s.check.write(f'{args["tmp_path"]}/test.csv', index=False)
