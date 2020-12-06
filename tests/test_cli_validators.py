import click
import pytest

from jira_teamlead.__main__ import validate_jira_host, validate_user


@pytest.mark.parametrize("value", ("", "lol", "lol:wut:lol", ":lol", "wut:", "лол:што"))
def test_validate_user_fail(value):
    with pytest.raises(click.BadParameter):
        validate_user(None, None, value)


def test_validate_user_ok():
    assert validate_user(None, None, "lol:wut") == "lol:wut"


@pytest.mark.parametrize("value", ("", "lol", "lol.wut.lol", "http:lol.wut"))
def test_validate_jira_host_fail(value):
    with pytest.raises(click.BadParameter):
        validate_jira_host(None, None, value)


@pytest.mark.parametrize(
    "value,expected",
    (
        ("http://lol.wut", "http://lol.wut"),
        ("https://lol.wut", "https://lol.wut"),
        ("http://lol.wut/lolwut", "http://lol.wut"),
        ("http://lol.wut?lol=wut", "http://lol.wut"),
    ),
)
def test_validate_jira_host_ok(value, expected):
    assert validate_jira_host(None, None, value) == expected
