from unittest import mock

import pytest

from jira_teamlead.cli.options.fallback import ConfigFallbackMixin, FallbackOption


@pytest.fixture
def config_mock():
    return mock.MagicMock()


@pytest.fixture
def ctx_mock():
    return mock.MagicMock()


@pytest.mark.parametrize(
    "option_kwargs,expected_param_hint",
    (
        ({}, "'--test'"),
        (
            {"config_parameter": ("section", "parameter")},
            "'mock_full_section.parameter = mock_value' (from mock_config_path)",
        ),
    ),
)
def test_get_error_hint(option_kwargs, expected_param_hint):
    config_fallback = FallbackOption(["--test"], **option_kwargs)
    config_fallback.from_config = True
    config_mock = mock.MagicMock()
    config_mock.path = "mock_config_path"
    config_mock.get_full_section_name.return_value = "mock_full_section"

    config_fallback.config = config_mock

    ctx_mock = mock.MagicMock()
    ctx_mock.params = {"test": "mock_value"}

    param_hint = config_fallback.get_error_hint(ctx=ctx_mock)

    assert param_hint == expected_param_hint


def test_value_from_config_no_config_parameter(ctx_mock):
    config_fallback = ConfigFallbackMixin(["--test"])

    value = config_fallback.value_from_config(ctx_mock)

    assert value is None


def test_value_from_config_if_config_is_none(ctx_mock):
    config_fallback = ConfigFallbackMixin(
        ["--test"], config_parameter=("section", "parameter")
    )

    ctx_mock.params = {"config": None}

    value = config_fallback.value_from_config(ctx_mock)

    assert value is None


def test_value_from_config_value_is_none(ctx_mock, config_mock):
    config_fallback = ConfigFallbackMixin(
        ["--test"], config_parameter=("section", "parameter")
    )

    config_mock.get.return_value = None
    ctx_mock.params = {"config": config_mock}

    value = config_fallback.value_from_config(ctx_mock)

    config_mock.get.assert_called_once_with("section", "parameter")

    assert value is None


def test_value_from_config_ok(ctx_mock, config_mock):
    config_fallback = ConfigFallbackMixin(
        ["--test"], config_parameter=("section", "parameter")
    )

    config_mock.get.return_value = "mock_value"
    ctx_mock.params = {"config": config_mock}

    value = config_fallback.value_from_config(ctx_mock)

    config_mock.get.assert_called_once_with("section", "parameter")

    assert value == "mock_value"
