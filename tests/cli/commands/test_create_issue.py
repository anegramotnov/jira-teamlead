from unittest import mock

from jira_teamlead.cli import create_issue


@mock.patch("jira_teamlead.cli.options.jira.JiraWrapper")
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
