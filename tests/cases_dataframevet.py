"""Assets used for test_dataframevet.py"""
import pandas as pd


# --------------------
# Dataframes to use as test cases
# Downloaded from https://github.com/mwaskom/seaborn-data
# on June 14 2024.
# --------------------
def df_anagrams():
    return pd.read_csv("tests/data/anagrams.csv")


def df_anscombe():
    return pd.read_csv("tests/data/anscombe.csv")


def df_attention():
    return pd.read_csv("tests/data/attention.csv")


def df_brain_networks():
    return pd.read_csv("tests/data/brain_networks.csv", header=[0, 1, 2])


def df_car_crashes():
    return pd.read_csv("tests/data/car_crashes.csv")


# def df_diamonds(): # Adding this case one doubles the total test time
#     return pd.read_csv('tests/data/diamonds.csv')
def df_dots():
    return pd.read_csv("tests/data/dots.csv")


def df_dowjones():
    return pd.read_csv("tests/data/dowjones.csv")


def df_exercise():
    return pd.read_csv("tests/data/exercise.csv")


def df_flights():
    return pd.read_csv("tests/data/flights.csv")


def df_fmri():
    return pd.read_csv("tests/data/fmri.csv")


def df_geyser():
    return pd.read_csv("tests/data/geyser.csv")


def df_glue():
    return pd.read_csv("tests/data/glue.csv")


def df_healthexp():
    return pd.read_csv("tests/data/healthexp.csv")


def df_iris():
    return pd.read_csv("tests/data/iris.csv")


def df_mpg():
    return pd.read_csv("tests/data/mpg.csv")


def df_penguins():
    return pd.read_csv("tests/data/penguins.csv")


def df_planets():
    return pd.read_csv("tests/data/planets.csv")


def df_seaice():
    return pd.read_csv("tests/data/seaice.csv")


def df_taxis():
    return pd.read_csv("tests/data/taxis.csv")


def df_tips():
    return pd.read_csv("tests/data/tips.csv")


def df_titanic():
    return pd.read_csv("tests/data/titanic.csv")


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
