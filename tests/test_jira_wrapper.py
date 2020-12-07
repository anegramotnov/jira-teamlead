from unittest import mock

from jira_teamlead.jira_wrapper import JiraWrapper, SubIssue, SuperIssue


@mock.patch("jira_teamlead.jira_wrapper.JIRA")
def test_search_users(JIRA_MOCK):

    user_1 = mock.MagicMock()
    user_1.name = "test"
    user_1.displayName = "Test test"
    user_1.emailAddress = "email at lol dot wut"
    user_1.deleted = False
    user_1.active = True

    user_2 = mock.MagicMock()
    user_2.name = "test 2"
    user_2.displayName = "Test test 2"
    user_2.emailAddress = "email2 at lol dot wut"
    user_2.deleted = True
    user_2.active = False

    jira_mock = JIRA_MOCK.return_value

    jira_mock.search_assignable_users_for_issues.return_value = [user_1, user_2]

    jira_wrapper = JiraWrapper(server="http://lol.wut", auth=("lol", "wut"))

    result = jira_wrapper.search_users(project="LOL")

    assert len(result) == 1

    assert result[0].lib_user == user_1

    jira_mock.search_assignable_users_for_issues.assert_called_once_with(
        username=None, project="LOL"
    )


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

    jira_wrapper = JiraWrapper(server="http://lol.wut", auth=("lol", "wut"))

    result = jira_wrapper.create_issue_set(
        issue_set=[
            {
                "summary": "Test issue",
                "issuetype": "Story",
                "description": "Test description",
                "sub_issues": [
                    {
                        "summary": "Test sub-issue",
                        "issuetype": "Task",
                    }
                ],
            }
        ],
        issue_template={"project": {"key": "LOL"}},
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
