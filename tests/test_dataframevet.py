import numpy as np
import pytest
from pandas.core.groupby.groupby import DataError
from pytest_cases import parametrize_with_cases

from pandas_vet import disable_checks, enable_checks, reset_format, start_timer


# Helper function
def assert_equal_df(df1, df2):
    # Since NaN!=NaN, make them strings
    if not (df1.fillna("NULL").eq(df2.fillna("NULL")).all().all()):
        raise AssertionError


@parametrize_with_cases("df", cases=".datasets", prefix="df_")
@parametrize_with_cases("test_method", prefix="method_")
@pytest.mark.parametrize("enable_checks_flag", [True, False])
def test_dataframevet_methods_dont_change_df(
    df, test_method, tmp_path, enable_checks_flag
):
    args = {
        "first_num_col": df.select_dtypes(include=["int64", "float64"]).columns[0],
        "tmp_path": tmp_path,
    }
    enable_checks() if enable_checks_flag else disable_checks()
    assert_equal_df(test_method(df, args), df)

    # Reset the environment for next tests
    enable_checks()
    reset_format()


def test_dataframevet_assert_data_pass(iris):
    # Shouldn't raise an exception
    iris.check.assert_data(
        condition=lambda df: df.sum() > 0,  # DF because we apply subset after.
        subset="sepal_length",  # This is atypical usage, but want to test the args work nonetheless
        raise_exception=True,
        exception_to_raise=ValueError,
    )


def test_dataframevet_assert_data_with_lambda_fn_fail(iris):
    with pytest.raises(ValueError):
        assert iris.check.assert_data(
            condition=lambda df: df["sepal_length"].sum() < 0,
            raise_exception=True,
            exception_to_raise=ValueError,
        )


def test_dataframevet_assert_data_with_str_fn_fail(iris):
    with pytest.raises(DataError):
        assert iris.check.assert_data(
            condition="df['sepal_length'].sum() < 0",
            raise_exception=True,
        )


def test_dataframevet_columns(iris, capsys):
    iris.check.columns(
        fn="df.assign(species_upper=df.species.str.upper())",
        subset=["petal_length", "species", "species_upper"],
    )
    assert (
        capsys.readouterr().out
        == "\n🏛️ Columns: ['petal_length', 'species', 'species_upper']\n"
    )


def test_dataframevet_describe(iris, capsys):
    iris.check.describe(
        fn=lambda df: (df * 2),
        subset=["petal_width", "species"],
        check_name="Test",
        include="all",
    )
    assert (
        capsys.readouterr().out
        == """\nTest
            petal_width       species
    count    150.000000           150
    unique          NaN             3
    top             NaN  setosasetosa
    freq            NaN            50
    mean       2.398667           NaN
    std        1.524475           NaN
    min        0.200000           NaN
    25%        0.600000           NaN
    50%        2.600000           NaN
    75%        3.600000           NaN
    max        5.000000           NaN\n"""
    )


def test_dataframevet_disable_checks(iris, capsys):
    (iris.check.disable_checks().check.nnulls())
    assert capsys.readouterr().out == ""
    enable_checks()  # reset


def test_dataframevet_dtypes(iris, capsys):
    iris.check.dtypes(fn=lambda df: df.select_dtypes("object"))
    assert (
        capsys.readouterr().out
        == """\n🗂️ Data types
    species    object\n"""
    )


def test_dataframevet_function_with_lambda_fn(iris, capsys):
    iris.check.function(fn=lambda df: len(df.columns), check_name="Test")
    assert capsys.readouterr().out == """\nTest: 5\n"""


def test_dataframevet_function_with_str_fn(iris, capsys):
    iris.check.function(fn="len(df.columns)", check_name="Test")
    assert capsys.readouterr().out == """\nTest: 5\n"""


def test_dataframevet_get_mode(iris, capsys):
    iris.check.get_mode(check_name="Test")
    assert (
        capsys.readouterr().out
        == """\nTest: {'enable_checks': True, 'enable_asserts': True}\n"""
    )


def test_dataframevet_head(iris, capsys):
    iris.check.head(n=1, fn=lambda df: (df * 2), check_name="Test")
    assert (
        capsys.readouterr().out
        == """\nTest
       sepal_length  sepal_width  petal_length  petal_width       species
    0          10.2          7.0           2.8          0.4  setosasetosa\n"""
    )


def test_dataframevet_hist_no_terminal_display(iris, capsys):
    iris.check.hist(subset=["sepal_width", "petal_length"])
    assert capsys.readouterr().out == ""


def test_dataframevet_info(iris, capsys):
    iris.check.info(
        fn=lambda df: (df * 2),
        subset=["petal_width", "species"],
        check_name="Test",
        memory_usage=True,
    )
    assert (
        capsys.readouterr().out
        == """\nTest
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 150 entries, 0 to 149
Data columns (total 2 columns):
 #   Column       Non-Null Count  Dtype
---  ------       --------------  -----
 0   petal_width  150 non-null    float64
 1   species      150 non-null    object
dtypes: float64(1), object(1)
memory usage: 2.5+ KB
"""
    )


def test_dataframevet_memory_usage(iris, capsys):
    iris.check.memory_usage(
        fn=lambda df: df[["petal_width", "species"]].dropna(),
        check_name="Test",
        deep=False,
    )
    assert (
        capsys.readouterr().out
        == """\nTest
    Index           128
    petal_width    1200
    species        1200\n"""
    )


def test_dataframevet_memory_usage_deep(iris, capsys):
    """Test that a kwarg is getting passed to Pandas's memory_usage()"""
    iris.check.memory_usage(
        fn=lambda df: df[["petal_width", "species"]].dropna(),
        check_name="Test",
        deep=True,
    )
    assert (
        capsys.readouterr().out
        == """\nTest
    Index           128
    petal_width    1200
    species        9800\n"""
    )


def test_dataframevet_ncols(iris, capsys):
    iris.check.ncols(
        fn=lambda df: df.assign(C=55), check_name="Test", subset=["C", "species"]
    )
    assert capsys.readouterr().out == "\nTest: 2\n"


def test_dataframevet_ndups(iris, capsys):
    iris.check.ndups(
        fn=lambda df: df.assign(C=55), check_name="Test", subset=["C", "species"]
    )
    assert capsys.readouterr().out == "\nTest: 147\n"


def test_dataframevet_ndups_keep(iris, capsys):
    """Test that a kwarg is getting passed to Pandas's memory_usage()"""
    iris.check.ndups(
        fn=lambda df: df.assign(C=55),
        check_name="Test",
        subset=["C", "species"],
        keep=False,
    )
    assert capsys.readouterr().out == "\nTest: 150\n"


def test_dataframevet_nnulls(iris, capsys):
    iris.check.nnulls(
        fn=lambda df: df.assign(C=np.nan), check_name="Test", by_column=False
    )
    assert capsys.readouterr().out == "\nTest: 150\n"


def test_dataframevet_nrows(iris, capsys):
    iris.check.nrows(
        fn=lambda df: df.assign(C=55), check_name="Test", subset=["C", "species"]
    )
    assert capsys.readouterr().out == "\nTest: 150\n"


def test_dataframevet_nunique(iris, capsys):
    iris.check.nunique(
        fn=lambda df: df.assign(C=55), check_name="Test", column="species", dropna=False
    )
    assert capsys.readouterr().out == "\nTest: 3\n"


def test_dataframevet_plot_no_terminal_display(iris, capsys):
    iris.check.plot(subset=["sepal_width", "petal_length"])
    assert capsys.readouterr().out == ""


def test_dataframevet_print_str(iris, capsys):
    iris.check.print("Howdy!")
    assert capsys.readouterr().out == "\nHowdy!\n"


def test_dataframevet_print_df(iris, capsys):
    iris.check.print(
        fn=lambda df: (df * 2).assign(species2=2),
        subset=[
            "sepal_length",
            "sepal_width",
            "petal_length",
            "petal_width",
            "species",
        ],
        check_name="Test",
        max_rows=1,
    )
    assert (
        capsys.readouterr().out
        == """\nTest
       sepal_length  sepal_width  petal_length  petal_width       species
    0          10.2          7.0           2.8          0.4  setosasetosa\n"""
    )


@pytest.mark.parametrize(
    "units_outputcontains",
    (
        ("auto", "seconds"),
        ("seconds", "seconds"),
        ("minutes", "minutes"),
        ("hours", "hours"),
    ),
)
def test_dataframevet_print_time_elapsed_units(iris, capsys, units_outputcontains):
    """We can't test the actual timings, since runtimes vary. So we'll test units"""
    units = units_outputcontains[0]
    output_contains = units_outputcontains[1]
    iris.check.print_time_elapsed(start_time=start_timer(), lead_in="Test", units=units)
    assert output_contains in capsys.readouterr().out


def test_dataframevet_reset_format(iris, capsys):
    (
        iris.check.set_format(precision=4, use_emojis=False)
        .check.reset_format()
        .check.print(
            fn=lambda df: (df * 2).assign(species2=2),
            subset=[
                "sepal_length",
                "sepal_width",
                "petal_length",
                "petal_width",
                "species",
            ],
            check_name="🧦 Sock",
            max_rows=1,
        )
    )
    assert (
        capsys.readouterr().out
        == """\n🧦 Sock
       sepal_length  sepal_width  petal_length  petal_width       species
    0          10.2          7.0           2.8          0.4  setosasetosa\n"""
    )


def test_dataframevet_set_format(iris, capsys):
    (
        iris.check.set_format(precision=10, use_emojis=False)
        .check.print(
            fn=lambda df: (df * 2).assign(species2=2),
            subset=[
                "sepal_length",
                "sepal_width",
                "petal_length",
                "petal_width",
                "species",
            ],
            check_name="🧦 Sock",
            max_rows=1,
        )
        .check.reset_format()
    )
    assert (
        capsys.readouterr().out
        == """\nSock
       sepal_length  sepal_width  petal_length  petal_width       species
    0          10.2          7.0           2.8          0.4  setosasetosa\n"""
    )


def test_dataframevet_set_mode(iris, capsys):
    (
        iris.check.set_mode(enable_checks=False, enable_asserts=False)
        .check.print("Howdy!")
        .check.assert_data(lambda df: len(df.columns) == 5)
        .check.set_mode(enable_checks=True, enable_asserts=True)  # Reset for next tests
    )
    assert capsys.readouterr().out == ""


def test_dataframevet_shape(iris, capsys):
    iris.check.shape(
        fn=lambda df: df.assign(C=55), check_name="Test", subset=["C", "species"]
    )
    assert capsys.readouterr().out == "\nTest: (150, 2)\n"


def test_dataframevet_tail(iris, capsys):
    iris.check.tail(n=1, fn=lambda df: (df * 2), check_name="Test")
    assert (
        capsys.readouterr().out
        == """\nTest
         sepal_length  sepal_width  petal_length  petal_width             species
    149          11.8          6.0          10.2          3.6  virginicavirginica\n"""
    )


def test_dataframevet_unique(iris, capsys):
    iris.check.unique(
        column="species",
        fn="df.assign(species_upper=df.species.str.upper())",
        check_name="🛼 Unique",
    )
    assert (
        capsys.readouterr().out == "\n🛼 Unique: ['setosa', 'versicolor', 'virginica']\n"
    )


def test_dataframevet_value_counts(iris, capsys):
    """Test that kwargs are getting passed to Pandas's value_counts()"""
    iris.check.value_counts(
        column="species",
        fn=lambda df: df.replace("setosa", None),
        check_name="Test",
        dropna=False,
        normalize=True,
    )
    assert (
        capsys.readouterr().out
        == """\nTest
    species
    None          0.333333
    versicolor    0.333333
    virginica     0.333333\n"""
    )


def test_dataframevet_write_csv(iris, tmp_path, capsys):
    """Test that kwargs are getting passed to Pandas's to_csv()"""
    iris.check.write(
        path=f"{tmp_path}/test.csv",
        fn=lambda df: df.dropna(),
        verbose=True,
        index=False,
    )
    assert capsys.readouterr().out == f"""\n📦 Wrote file {tmp_path}/test.csv\n"""
