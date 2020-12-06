import pytest

from jira_teamlead.jira import JiraServer


def test_auth_header():
    jira = JiraServer(host="http://lol.wut", auth_string="lol:wut")
    assert jira._get_auth_header() == {"Authorization": "Basic bG9sOnd1dA=="}


@pytest.mark.parametrize(
    "host,path,output",
    (
        ("http://lol.wut", "lolwut", "http://lol.wut/lolwut"),
        ("http://lol.wut/", "lolwut", "http://lol.wut/lolwut"),
        ("http://lol.wut", "/lolwut", "http://lol.wut/lolwut"),
        ("http://lol.wut", "lolwut/", "http://lol.wut/lolwut/"),
        ("http://lol.wut", "/lolwut/", "http://lol.wut/lolwut/"),
    ),
)
def test_get_url(host, path, output):
    jira = JiraServer(host=host, auth_string="lol:wut")

    assert jira._get_url(path) == output
