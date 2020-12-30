from pathlib import Path

import pytest

from jira_teamlead.issue_template import IssueTemplate

template_fields = {
    "project": {
        "key": "TEST",
    },
    "issuetype": {
        "name": "Bug",
    },
    "description": "Test description",
}


@pytest.mark.parametrize(
    "query,expected_result",
    (
        ("description", "Test description"),
        ("project.key", "TEST"),
        ("issuetype.name", "Bug"),
        ("", None),
        ("summary", None),
    ),
)
def test_get_template_ok(query, expected_result):
    template = IssueTemplate(path=Path(), fields=template_fields)

    result = template.get(query=query)

    assert result == expected_result
