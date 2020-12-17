from unittest import mock

import pytest

from jira_teamlead.cli.autocompletion import (
    assignee_autocompletion,
    is_empty_or_match,
    issue_type_autocompletion,
    project_autocompletion,
)
from jira_teamlead.jira_wrapper import IssueType, Project, User


@pytest.mark.parametrize(
    "search, name, result",
    (
        ("", "test", True),
        (None, "test", True),
        ("T", "Test", True),
        ("T", "test", True),
        ("t", "Test", True),
        ("Test", "tEST", True),
        ("T", "ftest", False),
        ("Test", "Tset", False),
        ("Tes", "Set", False),
    ),
)
def test_is_empty_or_match(search, name, result):
    assert is_empty_or_match(search, name) == result


@pytest.mark.parametrize(
    "search,result",
    (
        ("", ["Task", "Sub-task", "Bug", "Story"]),
        ("T", ["Task"]),
        ("S", ["Sub-task", "Story"]),
    ),
)
def test_issue_type_autocompletion(search, result):

    jira = mock.MagicMock()
    jira.get_issue_types.return_value = [
        IssueType(raw={}, id="10000", name="Task"),
        IssueType(raw={}, id="10001", name="Sub-task"),
        IssueType(raw={}, id="10002", name="Bug"),
        IssueType(raw={}, id="10003", name="Story"),
    ]

    autocompletion = issue_type_autocompletion(jira=jira, params={}, incomplete=search)

    assert autocompletion == result


def test_assignee_autocompletion():
    jira = mock.MagicMock()

    jira.search_users.return_value = [
        User(raw={}, name="lol.wut", displayName="", emailAddress=""),
        User(raw={}, name="wut.lol", displayName="", emailAddress=""),
    ]

    autocompletion = assignee_autocompletion(
        jira=jira, params={"project": "LOL"}, incomplete="wut?"
    )

    assert autocompletion == ["lol.wut", "wut.lol"]


@pytest.mark.parametrize(
    "search,result",
    (
        ("", ["LOL", "LOLWUT", "WUT"]),
        (None, ["LOL", "LOLWUT", "WUT"]),
        ("L", ["LOL", "LOLWUT"]),
        ("W", ["WUT"]),
        ("Laughing", ["LOL"]),
    ),
)
def test_project_autocompletion(search, result):
    jira = mock.MagicMock()

    jira.get_projects.return_value = [
        Project(raw={}, id="10000", key="LOL", name="Laughing Out Loud Project"),
        Project(raw={}, id="10001", key="LOLWUT", name="LOLWUT? project"),
        Project(raw={}, id="10002", key="WUT", name="WUT? Project"),
    ]

    autocompletion = project_autocompletion(jira=jira, params={}, incomplete=search)

    assert autocompletion == result
