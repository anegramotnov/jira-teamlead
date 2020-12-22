from unittest import mock

from jira_teamlead.cli import create_issue_set


@mock.patch("jira_teamlead.cli.options.jira.JiraWrapper")
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
