from pandas_vet.utils import _in_terminal, _lambda_to_string


def test__in_terminal_true_during_tests():
    """Tests are run in noninteractive mode"""
    assert _in_terminal() == True
