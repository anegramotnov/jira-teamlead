import shutil
from pathlib import Path
from unittest import mock

from jira_teamlead.cli import create_issue_set


def test_create_issue_set(jira_mock, cli, datadir):
    jira_mock.server = "http://lol.wut"

    issue_mock = mock.MagicMock()
    issue_mock.key = "LOL-1"

    jira_mock.create_issue_set.return_value = [issue_mock]

    shutil.copy(datadir / "test_issues.yaml", Path() / "test_issues.yaml")

    result = cli.invoke(
        create_issue_set,
        [
            "-js",
            "http://lol.wut",
            "-jl",
            "lol",
            "-jp",
            "wut",
            "--no-open",
            "test_issues.yaml",
        ],
    )
    assert result.exit_code == 0
    assert result.output == "Created issue: http://lol.wut/browse/LOL-1\n"
    jira_mock.create_issue_set.assert_called_once_with(
        issue_set=[
            {
                "summary": "Test Summary",
                "issuetype": {"name": "Lol"},
                "jtl_sub_issues": [{"summary": "Test Sub Summary"}],
            }
        ],
    )
