from functools import update_wrapper
from typing import Any, Callable, Optional
from urllib.parse import urlparse

import click

from jira_teamlead.cli.options import constants
from jira_teamlead.cli.options.config import from_config_fallback
from jira_teamlead.cli.options.fallback import FallbackOption
from jira_teamlead.jira_wrapper import JiraWrapper


def parse_server_option(
    ctx: click.Context, param: click.Parameter, value: Optional[str]
) -> Optional[str]:
    """Валидация и преобразование параметра --jira-host."""
    if value is None:
        return None

    url = urlparse(value)
    if not all([url.scheme, url.netloc]):
        raise click.BadParameter("ожидается формат 'http[s]://jira.host.net'")
    return f"{url.scheme}://{url.netloc}"


jira_options = (
    click.option(
        constants.SERVER_SHORT,
        constants.SERVER_FULL,
        constants.SERVER_PARAM,
        cls=FallbackOption,
        fallback=from_config_fallback(*constants.SERVER_CONFIG),
        callback=parse_server_option,
        required=True,
        prompt=True,
        help=constants.SERVER_HELP,
    ),
    click.option(
        constants.LOGIN_SHORT,
        constants.LOGIN_FULL,
        constants.LOGIN_PARAM,
        cls=FallbackOption,
        fallback=from_config_fallback(*constants.LOGIN_CONFIG),
        required=True,
        prompt=True,
        help=constants.LOGIN_HELP,
    ),
    click.option(
        constants.PASSWORD_SHORT,
        constants.PASSWORD_FULL,
        constants.PASSWORD_PARAM,
        cls=FallbackOption,
        fallback=from_config_fallback(*constants.PASSWORD_CONFIG),
        required=True,
        prompt=True,
        hide_input=True,
        help=constants.PASSWORD_HELP,
    ),
)


def set_jira_to_params(params: dict) -> JiraWrapper:
    server = params.pop(constants.SERVER_PARAM)
    login = params.pop(constants.LOGIN_PARAM)
    password = params.pop(constants.PASSWORD_PARAM)
    jira = JiraWrapper(server=server, auth=(login, password))
    params[constants.JIRA_PARAM] = jira
    return jira


def add_jira_options(name: str) -> Callable:
    """Декоратор добавления параметров соединения к серверу.

    Добавляет параметры server, auth и передает в аргументы функции готовый объект
    соединения с Jira.
    """

    def decorator(f: Callable) -> Callable:
        for option in reversed(jira_options):
            f = option(f)

        def wrapper(**kwargs: Any) -> Any:
            set_jira_to_params(kwargs)
            f(**kwargs)

        return update_wrapper(wrapper, f)

    return decorator
