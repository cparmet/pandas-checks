from pytest import fixture

from .datasets import df_iris


@fixture
def iris():
    return df_iris()
