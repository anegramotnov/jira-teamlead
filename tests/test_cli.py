from unittest import mock

import pytest
from click.testing import CliRunner

from jira_teamlead.cli.issues_commands import create_issue, create_issue_set
from jira_teamlead.cli.users_commands import search_users


@pytest.fixture()
def runner() -> CliRunner:
    runner = CliRunner()
    return runner


@mock.patch("jira_teamlead.cli.jira_options.JiraWrapper")
def test_search_users(JIRA_MOCK, runner):

    user_1 = mock.MagicMock()
    user_1.name = "test"
    user_1.displayName = "Test test"
    user_1.emailAddress = "email at lol dot wut"

    jira_mock = JIRA_MOCK.return_value

    jira_mock.search_users.return_value = [user_1]

    result = runner.invoke(
        search_users, ["-js", "http://lol.wut", "-jl", "lol", "-jp", "wut", "-p", "LOL"]
    )
    assert result.exit_code == 0
    assert result.output == "test (Test test, email at lol dot wut)\n"

    jira_mock.search_users.assert_called_once_with(search_string=None, project="LOL")


@mock.patch("jira_teamlead.cli.jira_options.JiraWrapper")
def test_create_issue(JIRA_MOCK, runner):
    jira_mock = JIRA_MOCK.return_value

    issue_mock = mock.MagicMock()
    issue_mock.link = "http://lol.wut/browse/LOL-1"

    jira_mock.create_issue.return_value = issue_mock
    with mock.patch("jira_teamlead.config.Config.get") as get_from_config:
        get_from_config.return_value = None
        result = runner.invoke(
            create_issue,
            [
                "-js",
                "http://lol.wut",
                "-jl",
                "lol",
                "-jp",
                "wut",
                "-p",
                "LOL",
                "-t",
                "Lol",
                "-s",
                "test task",
                "--no-open",
            ],
        )
    assert result.exit_code == 0
    assert result.output == "Created issue: http://lol.wut/browse/LOL-1\n"

    jira_mock.create_issue.assert_called_once_with(
        fields={
            "project": {"key": "LOL"},
            "issuetype": {"name": "Lol"},
            "summary": "test task",
        },
        template=None,
    )


@mock.patch("jira_teamlead.cli.jira_options.JiraWrapper")
def test_create_issue_set(JIRA_MOCK, runner):
    jira_mock = JIRA_MOCK.return_value
    jira_mock.server = "http://lol.wut"

    issue_mock = mock.MagicMock()
    issue_mock.key = "LOL-1"

    jira_mock.create_issue_set.return_value = [issue_mock]

    issues_file_content = """
    jtl_template:
      project:
        key: "LOL"
    jtl_issues:
      - summary: "Test Summary"
        issuetype:
          name: Lol
        jtl_sub_issues:
          - summary: "Test Sub Summary"
    """
    with runner.isolated_filesystem():
        with open("test_issues.yaml", "w", encoding="utf-8") as f:
            f.write(issues_file_content)

        result = runner.invoke(
            create_issue_set,
            ["-js", "http://lol.wut", "-jl", "lol", "-jp", "wut", "test_issues.yaml"],
        )
        assert result.exit_code == 0
        assert result.output == "Created issue: http://lol.wut/browse/LOL-1\n"
        jira_mock.create_issue_set.assert_called_once_with(
            issues=[
                {
                    "summary": "Test Summary",
                    "issuetype": {"name": "Lol"},
                    "jtl_sub_issues": [{"summary": "Test Sub Summary"}],
                }
            ],
            template={"project": {"key": "LOL"}},
        )
