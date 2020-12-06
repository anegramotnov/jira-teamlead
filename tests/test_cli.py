from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

from jira_teamlead.cli import create_issue, create_issues, find_user
from jira_teamlead.jira import JiraServer


@pytest.fixture()
def request_mock() -> MagicMock:
    request_mock = MagicMock()
    JiraServer.request = request_mock
    return request_mock


@pytest.fixture()
def runner() -> CliRunner:
    runner = CliRunner()
    return runner


def test_find_users(runner, request_mock):
    result = runner.invoke(
        find_user, ["-jh", "http://lol.wut", "-u", "lol:wut", "-p", "LOL"]
    )

    request_mock.assert_called_once_with(
        method="GET",
        path="/rest/api/2/user/assignable/search",
        params={"project": "LOL", "username": None},
    )
    assert result.exit_code == 0


def test_create_issue(runner, request_mock):
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

    request_mock.assert_called_once_with(
        method="POST",
        path="/rest/api/2/issue",
        payload={
            "fields": {
                "project": {"key": "LOL"},
                "issuetype": {"name": "Lol"},
                "summary": "test task",
            }
        },
    )
    assert result.exit_code == 0


def test_create_issues(runner, request_mock):
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
        request_mock.assert_called_once_with(
            method="POST",
            path="/rest/api/2/issue",
            payload={
                "fields": {
                    "summary": "Test Summary",
                    "issuetype": {"name": "Lol"},
                    "project": {"key": "LOL"},
                }
            },
        )
        assert result.exit_code == 0
