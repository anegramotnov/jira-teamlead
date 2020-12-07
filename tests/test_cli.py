from unittest import mock

import pytest
from click.testing import CliRunner

from jira_teamlead.cli import create_issue, create_issues, find_user


@pytest.fixture()
def runner() -> CliRunner:
    runner = CliRunner()
    return runner


@mock.patch("jira_teamlead.cli.jira_lib.JIRA")
def test_find_users(JIRA_MOCK, runner):

    user_1 = mock.MagicMock()
    user_1.name = "test"
    user_1.displayName = "Test test"
    user_1.emailAddress = "email at lol dot wut"
    user_1.deleted = False
    user_1.active = True

    jira_mock = JIRA_MOCK.return_value

    jira_mock.search_assignable_users_for_issues.return_value = [user_1]

    result = runner.invoke(
        find_user, ["-jh", "http://lol.wut", "-u", "lol:wut", "-p", "LOL"]
    )

    jira_mock.search_assignable_users_for_issues.assert_called_once_with(
        username=None, project="LOL"
    )
    assert result.exit_code == 0
    assert result.output == "test (Test test, email at lol dot wut)\n"


@mock.patch("jira_teamlead.cli.jira_lib.JIRA")
def test_create_issue(JIRA_MOCK, runner):
    jira_mock = JIRA_MOCK.return_value

    issue_mock = mock.MagicMock()
    issue_mock.key = "LOL-1"

    jira_mock.create_issue.return_value = issue_mock

    result = runner.invoke(
        create_issue,
        [
            "-jh",
            "http://lol.wut",
            "-u",
            "lol:wut",
            "-p",
            "LOL",
            "-t",
            "Lol",
            "-s",
            "test task",
        ],
    )

    jira_mock.create_issue.assert_called_once_with(
        issuetype={"name": "Lol"}, project={"key": "LOL"}, summary="test task"
    )
    assert result.exit_code == 0
    assert result.output == "Created issue: http://lol.wut/browse/LOL-1\n"


@mock.patch("jira_teamlead.cli.jira_lib.JIRA")
def test_create_issues(JIRA_MOCK, runner):
    jira_mock = JIRA_MOCK.return_value

    issue_mock = mock.MagicMock()
    issue_mock.key = "LOL-1"

    jira_mock.create_issue.return_value = issue_mock

    issues_file_content = """
    project:
      key: "LOL"
    issues:
      - summary: "Test Summary"
        issuetype:
          name: Lol
    """
    with runner.isolated_filesystem():
        with open("issues2.yaml", "w", encoding="utf-8") as f:
            f.write(issues_file_content)

        result = runner.invoke(
            create_issues, ["-jh", "http://lol.wut", "-u", "lol:wut", "issues2.yaml"]
        )
        jira_mock.create_issue.assert_called_once_with(
            issuetype={"name": "Lol"}, project={"key": "LOL"}, summary="Test Summary"
        )
        assert result.exit_code == 0
        assert result.output == "Created issue: http://lol.wut/browse/LOL-1\n"
