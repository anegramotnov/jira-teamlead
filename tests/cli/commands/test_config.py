from pathlib import Path
from unittest import mock

import pytest

from jira_teamlead.cli.commands.config import config_init, config_set


@pytest.mark.parametrize("command", (config_init, config_set))
def test_required_config_location_flag(cli, command):
    result = cli.invoke(command)
    assert result.exit_code == 2
    assert "Missing option '--local' / '--global'." in result.output


def test_init_required_options_ok(cli, datadir):
    options = [
        "--local",
        "--server",
        "http://localhost:8080",
        "--login",
        "test_login",
        "--password",
        "test_password",
        "--project",
        "TEST",
        "--open",
    ]
    result = cli.invoke(config_init, options)
    assert result.exit_code == 0

    local_config = Path() / ".jtl.cfg"
    reference_config = datadir / "required_options.cfg"
    assert local_config.read_text() == reference_config.read_text()


@mock.patch("jira_teamlead.cli.commands.config.get_global_config_path")
def test_init_global_ok(get_global_config_path, cli, datadir):
    get_global_config_path.return_value = Path() / ".jtl.cfg"

    options = [
        "--global",
        "--server",
        "http://localhost:8080",
        "--login",
        "test_login",
        "--password",
        "test_password",
        "--project",
        "TEST",
        "--open",
    ]
    result = cli.invoke(config_init, options)
    assert result.exit_code == 0

    local_config = Path() / ".jtl.cfg"
    reference_config = datadir / "required_options.cfg"
    assert local_config.read_text() == reference_config.read_text()


def test_init_all_options_ok(cli, datadir):
    options = [
        "--local",
        "--server",
        "http://localhost:8080",
        "--login",
        "test_login",
        "--password",
        "test_password",
        "--project",
        "TEST",
        "--template",
        "issue.yaml",
        "--open",
    ]
    result = cli.invoke(config_init, options)
    assert result.exit_code == 0
    assert result.output == ""

    local_config = Path() / ".jtl.cfg"
    reference_config = datadir / "all_options.cfg"
    assert local_config.read_text() == reference_config.read_text()


def test_set_template(cli, datadir):
    init_options = [
        "--local",
        "--server",
        "http://localhost:8080",
        "--login",
        "test_login",
        "--password",
        "test_password",
        "--project",
        "TEST",
        "--open",
    ]
    result = cli.invoke(config_init, init_options)

    assert result.exit_code == 0
    assert result.output == ""

    local_config = Path() / ".jtl.cfg"
    reference_config = datadir / "required_options.cfg"
    assert local_config.read_text() == reference_config.read_text()

    set_options = [
        "--local",
        "--template",
        "issue.yaml",
    ]

    result = cli.invoke(config_set, set_options)

    assert result.exit_code == 0
    assert result.output == ""

    reference_config = datadir / "after_add_template.cfg"
    assert local_config.read_text() == reference_config.read_text()
