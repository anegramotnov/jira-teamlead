from unittest import mock

from jira_teamlead.cli import search_users


def test_search_users(jira_mock, cli):

    user_1 = mock.MagicMock()
    user_1.name = "test"
    user_1.displayName = "Test test"
    user_1.emailAddress = "email at lol dot wut"

    jira_mock.search_users.return_value = [user_1]

    result = cli.invoke(
        search_users, ["-js", "http://lol.wut", "-jl", "lol", "-jp", "wut", "-p", "LOL"]
    )
    assert result.exit_code == 0
    assert result.output == "test (Test test, email at lol dot wut)\n"

    jira_mock.search_users.assert_called_once_with(search_string=None, project="LOL")
