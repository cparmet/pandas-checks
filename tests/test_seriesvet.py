import numpy as np
import pandas as pd
import pytest
from pandas.core.groupby.groupby import DataError
from pytest_cases import parametrize_with_cases

from pandas_vet import disable_checks, enable_checks, reset_format, start_timer


# Helper functions
def assert_equal_series(s1, s2):
    # Since NaN!=NaN, make them strings
    if not (s1.fillna("NULL").eq(s2.fillna("NULL")).all()):
        raise AssertionError


def strip_multiline(s):
    """Strip the whitespace from multiline strings. Used to facilitate assertions of stdout

    For example, with _ indicating white space:
        '''Hello ___
           my friend!
        '''
        becomes
        '''Hello
           my friend!
        '''
    """
    return "\n".join([line.strip() for line in s.splitlines()])


def assert_multiline_string_equal(s1, s2):
    assert strip_multiline(s1) == strip_multiline(s2)


@parametrize_with_cases("df", cases=".datasets", prefix="df_")
@parametrize_with_cases("test_method", prefix="method_")
@pytest.mark.parametrize("enable_checks_flag", [True, False])
def test_seriesvet_methods_dont_change_series(
    df, test_method, tmp_path, enable_checks_flag
):
    if not enable_checks_flag:
        disable_checks()
    for col in df.columns:
        assert_equal_series(
            s1=test_method(df[col], {"tmp_path": tmp_path}), s2=df[col]  # Args
        )
    enable_checks()
    reset_format()


def test_seriesvet_assert_data_pass(iris):
    # Shouldn't raise an exception
    (
        iris["sepal_length"].check.assert_data(
            condition=lambda s: s.sum() > 0,
            raise_exception=True,
            exception_to_raise=ValueError,
        )
    )


def test_seriesvet_assert_data_fail(iris):
    with pytest.raises(DataError):
        assert iris["sepal_length"].check.assert_data(
            condition=lambda s: s.sum() < 0,
            raise_exception=True,
        )


def test_seriesvet_assert_data_custom_exception_fail(iris):
    with pytest.raises(ValueError):
        assert iris["sepal_length"].check.assert_data(
            condition=lambda s: s.sum() < 0,
            raise_exception=True,
            exception_to_raise=ValueError,
        )


def test_seriesvet_describe(iris, capsys):
    (
        iris["petal_width"].check.describe(
            fn=lambda s: (s * 2),
            check_name="Test",
            include="all",
        )
    )
    assert_multiline_string_equal(
        capsys.readouterr().out,
        """\nTest
           petal_width
    count   150.000000
    mean      2.398667
    std       1.524475
    min       0.200000
    25%       0.600000
    50%       2.600000
    75%       3.600000
    max       5.000000\n""",
    )


def test_seriesvet_disable_checks(iris, capsys):
    (iris.check.disable_checks().check.nnulls())
    assert capsys.readouterr().out == ""
    enable_checks()  # reset


def test_seriesvet_dtype(iris, capsys):
    iris["species"].check.dtype()
    assert capsys.readouterr().out == """\n🗂️ Data type: object\n"""


def test_seriesvet_function(iris, capsys):
    iris["species"].check.function(fn=lambda s: s.shape[0], check_name="Test")
    assert capsys.readouterr().out == """\nTest: 150\n"""


def test_seriesvet_get_mode(iris, capsys):
    iris.check.get_mode(check_name="Test")
    assert (
        capsys.readouterr().out
        == """\nTest: {'enable_checks': True, 'enable_asserts': True}\n"""
    )


def test_seriesvet_head(iris, capsys):
    iris["sepal_length"].check.head(n=1, fn=lambda s: (s * 2), check_name="Test")
    assert_multiline_string_equal(
        capsys.readouterr().out,
        """\nTest
       sepal_length
    0          10.2\n""",
    )


def test_seriesvet_hist_no_terminal_display(iris, capsys):
    iris["sepal_width"].check.hist()
    assert capsys.readouterr().out == ""


def test_seriesvet_info(iris, capsys):
    iris["petal_width"].check.info(
        fn=lambda s: (s * 2),
        check_name="Test",
        memory_usage=True,
    )
    assert_multiline_string_equal(
        capsys.readouterr().out,
        """\nTest
<class 'pandas.core.series.Series'>
RangeIndex: 150 entries, 0 to 149
Series name: petal_width
Non-Null Count  Dtype
--------------  -----
150 non-null    float64
dtypes: float64(1)
memory usage: 1.3 KB
""",
    )


def test_seriesvet_memory_usage(iris, capsys):
    (
        iris["petal_width"].check.memory_usage(
            fn=lambda s: s.dropna(),
            check_name="Test",
            deep=False,
        )
    )
    assert_multiline_string_equal(
        capsys.readouterr().out,
        """\nTest
    Index          1200
    petal_width    1200\n""",
    )


def test_seriesvet_memory_usage_deep(iris, capsys):
    """Test that a kwarg is getting passed to Pandas's memory_usage()"""
    iris["species"].check.memory_usage(
        fn=lambda s: s.dropna(),
        check_name="Test",
        deep=True,
    )
    assert_multiline_string_equal(
        capsys.readouterr().out,
        """\nTest
    Index      1200
    species    9800\n""",
    )


def test_seriesvet_ndups(iris, capsys):
    iris["species"].check.ndups(fn=lambda s: s.dropna(), check_name="Test")
    assert capsys.readouterr().out == "\nTest: 147\n"


def test_seriesvet_ndups_keep(iris, capsys):
    """Test that a kwarg is getting passed to Pandas's memory_usage()"""
    iris["species"].check.ndups(
        fn=lambda s: s.dropna(),
        check_name="Test",
        keep=False,
    )
    assert capsys.readouterr().out == "\nTest: 150\n"


def test_seriesvet_nnulls(iris, capsys):
    iris["species"].check.nnulls(
        fn=lambda s: s.replace("versicolor", np.nan),
        check_name="Test",
    )
    assert capsys.readouterr().out == "\nTest: 50\n"


def test_seriesvet_nrows(iris, capsys):
    iris["species"].check.nrows(fn=lambda s: s[s == "versicolor"], check_name="Test")
    assert capsys.readouterr().out == "\nTest: 50\n"


def test_seriesvet_nunique(iris, capsys):
    iris["species"].check.nunique(
        fn=lambda s: s[s != "versicolor"], check_name="Test", dropna=False
    )
    assert capsys.readouterr().out == "\nTest: 2\n"


def test_seriesvet_plot_no_terminal_display(iris, capsys):
    iris["sepal_width"].check.plot()
    assert capsys.readouterr().out == ""


def test_seriesvet_print_str(iris, capsys):
    iris.check.print("Howdy!")
    assert capsys.readouterr().out == "\nHowdy!\n"


def test_seriesvet_print_series(iris, capsys):
    iris["sepal_length"].check.print(
        fn=lambda s: s * 2,
        check_name="Test",
        max_rows=1,
    )
    assert_multiline_string_equal(
        capsys.readouterr().out,
        """\nTest
       sepal_length
    0          10.2\n""",
    )


@pytest.mark.parametrize(
    "units_outputcontains",
    (
        ("auto", "milliseconds"),
        ("milliseconds", "milliseconds"),
        ("ms", "ms"),
        ("seconds", "seconds"),
        ("s", "s"),
        ("minutes", "minutes"),
        ("m", "m"),
        ("hours", "hours"),
        ("h", "h"),
    ),
)
def test_seriesvet_print_time_elapsed_units(iris, capsys, units_outputcontains):
    """We can't test the actual timings, since runtimes vary. So we'll test units"""
    units = units_outputcontains[0]
    output_contains = units_outputcontains[1]
    (
        iris["sepal_length"].check.print_time_elapsed(
            start_time=start_timer(), lead_in="Test", units=units
        )
    )
    assert output_contains in capsys.readouterr().out


def test_seriesvet_reset_format(iris, capsys):
    (
        iris["sepal_length"]
        .check.set_format(precision=4, use_emojis=False)
        .check.reset_format()
        .check.print(
            fn=lambda s: s * 2,
            check_name="🧦 Sock",
            max_rows=1,
        )
    )
    assert_multiline_string_equal(
        capsys.readouterr().out,
        """\n🧦 Sock
       sepal_length
    0          10.2\n""",
    )


def test_seriesvet_set_format(iris, capsys):
    (
        iris["sepal_length"]
        .check.set_format(precision=10, use_emojis=False)
        .check.print(
            fn=lambda s: s * 2,
            check_name="🧦 Sock",
            max_rows=1,
        )
        .check.reset_format()
    )
    assert_multiline_string_equal(
        capsys.readouterr().out,
        """\nSock
       sepal_length
    0          10.2\n""",
    )


def test_seriesvet_set_mode(iris, capsys):
    (
        iris["sepal_length"]
        .check.set_mode(enable_checks=False, enable_asserts=False)
        .check.print("Howdy!")
        .check.assert_data(lambda s: s.shape[0] == 5)
        .check.set_mode(enable_checks=True, enable_asserts=True)  # Reset for next tests
    )
    assert capsys.readouterr().out == ""


def test_seriesvet_shape(iris, capsys):
    iris["sepal_width"].check.shape(
        fn=lambda s: pd.concat([s, s], ignore_index=True, axis=0), check_name="Test"
    )
    assert capsys.readouterr().out == "\nTest: (300,)\n"


def test_seriesvet_tail(iris, capsys):
    (iris["sepal_length"].check.tail(n=1, fn=lambda s: s * 2, check_name="Test"))
    assert_multiline_string_equal(
        capsys.readouterr().out,
        """\nTest
         sepal_length
    149          11.8\n""",
    )


def test_seriesvet_unique(iris, capsys):
    iris["species"].check.unique(
        fn=lambda s: s.str.upper(),
        check_name="🛼 Unique",
    )
    assert (
        capsys.readouterr().out == "\n🛼 Unique: ['SETOSA', 'VERSICOLOR', 'VIRGINICA']\n"
    )


def test_seriesvet_value_counts(iris, capsys):
    """Test that kwargs are getting passed to Pandas's value_counts()"""
    iris["species"].check.value_counts(
        fn=lambda s: s.replace("setosa", None),
        check_name="Test",
        dropna=False,
        normalize=True,
    )
    assert_multiline_string_equal(
        capsys.readouterr().out,
        """\nTest
    species
    None          0.333333
    versicolor    0.333333
    virginica     0.333333\n""",
    )


@pytest.mark.parametrize(
    "format_extension",
    (
        ("csv", "csv"),
        ("xlsx", "xlsx"),
        ("excel", "xlsx"),
        ("parquet", "parquet"),
        ("feather", "feather"),
        ("pkl", "pkl"),
        ("pickle", "pkl"),
        ("tsv", "tsv"),
    ),
)
def test_seriesvet_write(iris, format_extension, tmp_path, capsys):
    extension = format_extension[1]
    f = lambda s: s[s == "versicolor"].reset_index()  # Reset is for Feather
    path = f"{tmp_path}/test.{extension}"
    series = iris["species"]
    series.check.write(
        path=path,
        fn=f,
        verbose=True,
    )
    assert capsys.readouterr().out == f"""\n📦 Wrote file {path}\n"""

    if extension == "csv":
        assert_equal_series(
            f(series)["species"], pd.read_csv(path, index_col=0)["species"]
        )
    elif extension == "xlsx":
        assert_equal_series(
            f(series)["species"], pd.read_excel(path, index_col=0)["species"]
        )
    elif extension == "feather":
        assert_equal_series(f(series)["species"], pd.read_feather(path)["species"])
    elif extension == "parquet":
        assert_equal_series(f(series)["species"], pd.read_parquet(path)["species"])
    elif extension == "pkl":
        assert_equal_series(f(series)["species"], pd.read_pickle(path)["species"])
    elif extension == "tsv":
        assert_equal_series(
            f(series)["species"], pd.read_csv(path, sep="\t", index_col=0)["species"]
        )
