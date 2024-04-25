import pytest

session_permanent = pytest.mark.parametrize(
    '_session_permanent',
    [True, False],
)
session_refresh_each_request = pytest.mark.parametrize(
    '_session_refresh_each_request',
    [True, False],
)
