import click
import pytest

from jira_teamlead.cli.validators import parse_auth_option, parse_server_option


@pytest.mark.parametrize("value", ("", "lol", "lol:wut:lol", ":lol", "wut:", "лол:што"))
def test_parse_auth_fail(value):
    with pytest.raises(click.BadParameter):
        parse_auth_option(None, None, value)


def test_parse_auth_ok():
    assert parse_auth_option(None, None, "lol:wut") == ("lol", "wut")


@pytest.mark.parametrize("value", ("", "lol", "lol.wut.lol", "http:lol.wut"))
def test_parse_server_fail(value):
    with pytest.raises(click.BadParameter):
        parse_server_option(None, None, value)


@pytest.mark.parametrize(
    "value,expected",
    (
        ("http://lol.wut", "http://lol.wut"),
        ("https://lol.wut", "https://lol.wut"),
        ("http://lol.wut/lolwut", "http://lol.wut"),
        ("http://lol.wut?lol=wut", "http://lol.wut"),
    ),
)
def test_parse_server_ok(value, expected):
    assert parse_server_option(None, None, value) == expected
