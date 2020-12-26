from unittest import mock

import pytest
from click.testing import CliRunner


@pytest.fixture()
def cli():
    runner = CliRunner()
    with runner.isolated_filesystem():
        yield runner


@pytest.fixture
def jira_mock():
    with mock.patch("jira_teamlead.cli.options.jira.JiraWrapper") as JiraWrapper:
        jira_mock = JiraWrapper.return_value
        yield jira_mock


@pytest.fixture
def config_get_mock():
    with mock.patch("jira_teamlead.config.Config.get") as config_get_mock:
        yield config_get_mock


@pytest.fixture
def config_mock():
    with mock.patch("jira_teamlead.config.Config") as config_mock:
        yield config_mock
