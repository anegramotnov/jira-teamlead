from functools import update_wrapper
from typing import Any, Callable

import click

from jira_teamlead.cli.config import try_get_from_config
from jira_teamlead.cli.validators import parse_auth_option, parse_server_option
from jira_teamlead.jira_wrapper import JiraWrapper

jira_options = (
    click.option(
        "-js",
        "--server",
        callback=try_get_from_config(
            parse_server_option, section="jira", option="server", required=True
        ),
        help="Cервер Jira",
    ),
    click.option(
        "-ja",
        "--auth",
        callback=try_get_from_config(
            parse_auth_option, section="jira", option="auth", required=True
        ),
        help="Учетные данные в формате 'login:password'",
    ),
)


def set_jira_to_params(params: dict) -> None:
    server = params.pop("server")
    auth = params.pop("auth")
    params["jira"] = JiraWrapper(server=server, auth=auth)


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
