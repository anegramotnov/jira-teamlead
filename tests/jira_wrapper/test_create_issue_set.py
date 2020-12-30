from unittest import mock

from jira_teamlead.jira_wrapper import Jira, SubIssue, SuperIssue


@mock.patch("jira_teamlead.jira_wrapper.JIRA")
def test_create_issue_set(JIRA_MOCK):
    jira_mock = JIRA_MOCK.return_value

    sub_issue = mock.MagicMock(
        fields=mock.MagicMock(summary="Test sub-issue"),
        key="LOL-2",
    )

    super_issue = mock.MagicMock(
        fields=mock.MagicMock(summary="Test issue"),
        key="LOL-1",
    )

    jira_mock.create_issue.side_effect = [super_issue, sub_issue]

    jira_wrapper = Jira(server="http://lol.wut", auth=("lol", "wut"))

    result = jira_wrapper.create_issue_set(
        issue_set=[
            {
                "summary": "Test issue",
                "issuetype": "Story",
                "description": "Test description",
                "jtl_sub_issues": [
                    {
                        "summary": "Test sub-issue",
                        "issuetype": "Task",
                    }
                ],
            }
        ],
    )

    assert len(result) == 1

    result_super_issue = result[0]
    assert isinstance(result_super_issue, SuperIssue)
    assert result_super_issue.key == "LOL-1"
    assert result_super_issue.summary == "Test issue"
    assert len(result_super_issue.sub_issues) == 1

    result_sub_issue = result_super_issue.sub_issues[0]

    assert isinstance(result_sub_issue, SubIssue)
    assert result_sub_issue.key == "LOL-2"
    assert result_sub_issue.summary == "Test sub-issue"

    assert jira_mock.create_issue.call_count == 2
