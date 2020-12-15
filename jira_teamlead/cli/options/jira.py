from functools import update_wrapper
from typing import Any, Callable
from urllib.parse import urlparse

import click

from jira_teamlead.cli.options.config import from_config_fallback
from jira_teamlead.cli.options.fallback import FallbackOption
from jira_teamlead.jira_wrapper import JiraWrapper

SERVER_CLICK_PARAM = "server"
LOGIN_CLICK_PARAM = "login"
PASSWORD_CLICK_PARAM = "password"
JIRA_CLICK_PARAM = "jira"


def parse_server_option(ctx: click.Context, param: click.Parameter, value: str) -> str:
    """Валидация и преобразование параметра --jira-host."""
    url = urlparse(value)

    if not all([url.scheme, url.netloc]):
        raise click.BadParameter("ожидается формат 'http[s]://jira.host.net'")

    return f"{url.scheme}://{url.netloc}"


jira_options = (
    click.option(
        "-js",
        "--server",
        SERVER_CLICK_PARAM,
        cls=FallbackOption,
        fallback=from_config_fallback(section="jira", option=SERVER_CLICK_PARAM),
        callback=parse_server_option,
        required=True,
        prompt=True,
        help="Cервер Jira",
    ),
    click.option(
        "-jl",
        "--login",
        LOGIN_CLICK_PARAM,
        cls=FallbackOption,
        fallback=from_config_fallback(section="jira", option=LOGIN_CLICK_PARAM),
        required=True,
        prompt=True,
        help="Логин в Jira",
    ),
    click.option(
        "-jp",
        "--password",
        PASSWORD_CLICK_PARAM,
        cls=FallbackOption,
        fallback=from_config_fallback(section="jira", option=PASSWORD_CLICK_PARAM),
        required=True,
        prompt=True,
        hide_input=True,
        help="Пароль в Jira",
    ),
)


def set_jira_to_params(params: dict) -> None:
    server = params.pop(SERVER_CLICK_PARAM)
    login = params.pop(LOGIN_CLICK_PARAM)
    password = params.pop(PASSWORD_CLICK_PARAM)
    params[JIRA_CLICK_PARAM] = JiraWrapper(server=server, auth=(login, password))


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
