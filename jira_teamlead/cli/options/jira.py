from functools import update_wrapper
from typing import Any, Callable, Optional
from urllib.parse import urlparse

import click

from jira_teamlead.cli.options import constants as c
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
        c.SERVER_SHORT,
        c.SERVER_FULL,
        c.SERVER_PARAM,
        cls=FallbackOption,
        config_parameter=c.SERVER_CONFIG,
        callback=parse_server_option,
        required=True,
        prompt=c.SERVER_HELP,
        help=c.SERVER_HELP,
    ),
    click.option(
        c.LOGIN_SHORT,
        c.LOGIN_FULL,
        c.LOGIN_PARAM,
        cls=FallbackOption,
        config_parameter=c.LOGIN_CONFIG,
        required=True,
        prompt=c.LOGIN_HELP,
        help=c.LOGIN_HELP,
    ),
    click.option(
        c.PASSWORD_SHORT,
        c.PASSWORD_FULL,
        c.PASSWORD_PARAM,
        cls=FallbackOption,
        config_parameter=c.PASSWORD_CONFIG,
        required=True,
        prompt=c.PASSWORD_HELP,
        hide_input=True,
        help=c.PASSWORD_HELP,
    ),
)


def set_jira_to_params(params: dict) -> JiraWrapper:
    server = params.pop(c.SERVER_PARAM)
    login = params.pop(c.LOGIN_PARAM)
    password = params.pop(c.PASSWORD_PARAM)
    jira = JiraWrapper(server=server, auth=(login, password))
    params[c.JIRA_PARAM] = jira
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
