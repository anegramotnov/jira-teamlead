import click
import pytest

from jira_teamlead.cli import validate_jira_auth, validate_jira_server


@pytest.mark.parametrize("value", ("", "lol", "lol:wut:lol", ":lol", "wut:", "лол:што"))
def test_validate_user_fail(value):
    with pytest.raises(click.BadParameter):
        validate_jira_auth(None, None, value)


def test_validate_user_ok():
    assert validate_jira_auth(None, None, "lol:wut") == ("lol", "wut")


@pytest.mark.parametrize("value", ("", "lol", "lol.wut.lol", "http:lol.wut"))
def test_validate_jira_host_fail(value):
    with pytest.raises(click.BadParameter):
        validate_jira_server(None, None, value)


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
    assert validate_jira_server(None, None, value) == expected
