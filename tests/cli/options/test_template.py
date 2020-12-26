import pytest

from jira_teamlead.cli.options.template import get_from_template

default_template = {
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
    result = get_from_template(query=query, template=default_template)
    assert result == expected_result
