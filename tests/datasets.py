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


# def df_diamonds():  # Note: adding this case one 3x's the total test time
#     return pd.read_csv("tests/data/diamonds.csv")


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
