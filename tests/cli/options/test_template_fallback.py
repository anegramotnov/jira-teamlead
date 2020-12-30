from pathlib import Path
from unittest import mock

import pytest

from jira_teamlead.cli.options.fallback import TemplateFallbackMixin
from jira_teamlead.issue_template import IssueTemplate


@pytest.fixture
def ctx_mock():
    return mock.MagicMock()


def test_value_from_template_no_template_query(ctx_mock):
    template_fallback = TemplateFallbackMixin(["--test"])

    value = template_fallback.value_from_template(ctx_mock)

    assert value is None


def test_value_from_template_if_template_is_none(ctx_mock):
    template_fallback = TemplateFallbackMixin(
        ["--test"], template_query="template.query"
    )

    ctx_mock.params = {}

    value = template_fallback.value_from_template(ctx_mock)

    assert value is None


def test_value_from_template_value_is_none(ctx_mock):
    template_fallback = TemplateFallbackMixin(
        ["--test"], template_query="template.query"
    )

    ctx_mock.params = {"issue_template": IssueTemplate(path=Path(), fields={})}

    value = template_fallback.value_from_template(ctx_mock)

    assert value is None


def test_value_from_template_is_none(ctx_mock):
    template_fallback = TemplateFallbackMixin(
        ["--test"], template_query="template.query"
    )

    ctx_mock.params = {
        "issue_template": IssueTemplate(
            path=Path(), fields={"template": {"query": "mock_value"}}
        )
    }

    value = template_fallback.value_from_template(ctx_mock)

    assert value == "mock_value"
