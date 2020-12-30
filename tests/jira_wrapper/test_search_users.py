from unittest import mock

from jira_teamlead.jira_wrapper import Jira


@mock.patch("jira_teamlead.jira_wrapper.JIRA")
def test_search_users(JIRA_MOCK):

    user_1 = mock.MagicMock()
    user_1.raw = {"raw_field": "raw_value"}
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

    jira_wrapper = Jira(server="http://lol.wut", auth=("lol", "wut"))

    result = jira_wrapper.search_users(project="LOL")

    assert len(result) == 1

    assert result[0].raw == user_1.raw

    jira_mock.search_assignable_users_for_issues.assert_called_once_with(
        username=None, project="LOL"
    )
