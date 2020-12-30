import shutil
from pathlib import Path
from unittest import mock

import pytest

from jira_teamlead.cli import create_issue
from jira_teamlead.jira_wrapper import JiraError

minimal_expected_fields = {
    "project": {"key": "TSTPRJ"},
    "issuetype": {"name": "Test Issue Type"},
    "summary": "test task",
}

full_expected_fields = {
    "project": {"key": "TSTPRJ"},
    "issuetype": {"name": "Test Issue Type"},
    "summary": "test task",
    "assignee": {"name": "test_login"},
}


def copy_files_to_current_dir(data_dir: Path):
    for f in data_dir.glob("*"):
        shutil.copy(f, Path() / f.name)


@pytest.fixture
def jira_with_issue(jira_mock):
    issue_mock = mock.MagicMock()
    issue_mock.link = "http://test.server/browse/TSTPRJ-1"

    jira_mock.create_issue.return_value = issue_mock

    yield jira_mock


@pytest.mark.parametrize(
    "params,expected_fields",
    (
        (
            [
                "-js",
                "http://test.server",
                "-jl",
                "test_login",
                "-jp",
                "test_password",
                "-p",
                "TSTPRJ",
                "-t",
                "Test Issue Type",
                "-s",
                "test task",
                "--no-open",
            ],
            minimal_expected_fields,
        ),
        (
            [
                "--server",
                "http://test.server",
                "--login",
                "test_login",
                "--password",
                "test_password",
                "--project",
                "TSTPRJ",
                "--type",
                "Test Issue Type",
                "--summary",
                "test task",
                "--no-open",
            ],
            minimal_expected_fields,
        ),
        (
            [
                "--config",
                "empty_config.cfg",
                "--server",
                "http://test.server",
                "--login",
                "test_login",
                "--password",
                "test_password",
                "--template",
                "empty_template.yaml",
                "--project",
                "TSTPRJ",
                "--type",
                "Test Issue Type",
                "--assignee",
                "test_login",
                "--summary",
                "test task",
                "--no-open",
            ],
            full_expected_fields,
        ),
    ),
    ids=("short_minimal_params", "minimal_params", "full_params"),
)
def test_options(
    jira_with_issue, config_get_mock, cli, params, expected_fields, datadir
):
    copy_files_to_current_dir(datadir)

    config_get_mock.return_value = None

    result = cli.invoke(create_issue, params)
    assert result.exit_code == 0
    assert result.output == "Created issue: http://test.server/browse/TSTPRJ-1\n"

    jira_with_issue.create_issue.assert_called_once_with(
        fields=expected_fields,
    )


@pytest.mark.parametrize(
    "params,config_name",
    (
        (
            [
                "--type",
                "Test Issue Type",
                "--summary",
                "test task",
            ],
            ".jtl.cfg",
        ),
        (
            [
                "--config",
                "custom_config.cfg",
                "--type",
                "Test Issue Type",
                "--summary",
                "test task",
            ],
            "custom_config.cfg",
        ),
    ),
    ids=("local_config", "custom_config"),
)
def test_with_config(cli, jira_with_issue, datadir, params, config_name):
    shutil.copy(datadir / "default_config.cfg", Path() / config_name)

    result = cli.invoke(create_issue, params)

    assert result.exit_code == 0
    assert result.output == "Created issue: http://test.server/browse/TSTPRJ-1\n"
    jira_with_issue.create_issue.assert_called_once_with(
        fields={
            "project": {"key": "TSTPRJ_FROM_CONFIG"},
            "issuetype": {"name": "Test Issue Type"},
            "summary": "test task",
        },
    )


def test_override_project_by_params(cli, jira_with_issue, datadir):
    shutil.copy(datadir / "default_config.cfg", Path() / ".jtl.cfg")

    params = [
        "--project",
        "TSTPRJ_FROM_PARAMS",
        "--type",
        "Test Issue Type",
        "--summary",
        "test task",
    ]

    result = cli.invoke(create_issue, params)

    assert result.exit_code == 0
    assert result.output == "Created issue: http://test.server/browse/TSTPRJ-1\n"
    jira_with_issue.create_issue.assert_called_once_with(
        fields={
            "project": {"key": "TSTPRJ_FROM_PARAMS"},
            "issuetype": {"name": "Test Issue Type"},
            "summary": "test task",
        },
    )


def test_with_template(cli, jira_with_issue, datadir):
    shutil.copy(datadir / "default_config.cfg", Path() / ".jtl.cfg")
    shutil.copy(datadir / "param_template.yaml", Path() / "param_template.yaml")

    params = ["--template", "param_template.yaml", "--summary", "summary from cli"]

    result = cli.invoke(create_issue, params)

    assert result.exit_code == 0
    assert result.output == "Created issue: http://test.server/browse/TSTPRJ-1\n"

    jira_with_issue.create_issue.assert_called_once_with(
        fields={
            "project": {"key": "OVERRIDED_BY_TEMPLATE"},
            "issuetype": {"name": "Issue Type From Template"},
            "summary": "summary from cli",
            "assignee": {"name": "login_from_template"},
            "customfield_10100": 1,
        },
    )


def test_jira_error(cli, jira_mock, datadir):
    shutil.copy(datadir / "default_config.cfg", Path() / ".jtl.cfg")

    jira_mock.create_issue.side_effect = JiraError(
        message="test error message",
        status_code=404,
        response={"errorMessages": ["test error message1"]},
    )

    params = [
        "--type",
        "Test Issue Type",
        "--summary",
        "test task",
    ]

    result = cli.invoke(create_issue, params)

    assert result.exit_code == 3
    assert "Jira REST API Error (404 Not Found):" in result.output
    assert "test error message1" in result.output


def test_jira_field_error(cli, jira_mock, datadir):
    shutil.copy(datadir / "default_config.cfg", Path() / ".jtl.cfg")

    jira_mock.create_issue.side_effect = JiraError(
        message="test error message2",
        status_code=400,
        response={
            "errorMessages": [],
            "errors": {"summary": "field error message"},
        },
    )

    params = [
        "--type",
        "Test Issue Type",
        "--summary",
        "test task",
    ]

    result = cli.invoke(create_issue, params)

    assert result.exit_code == 3
    assert "Jira REST API Error (400 Bad Request):" in result.output
    assert (
        "Invalid value for field '-s' / '--summary': \"field error message\""
        in result.output
    )
