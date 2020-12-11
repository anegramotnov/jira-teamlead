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


def add_jira_options(name: str) -> Callable:
    """Декоратор добавления параметров соединения к серверу.

    Добавляет параметры server, auth и передает в аргументы функции готовый объект
    соединения с Jira.
    """

    def decorator(f: Callable) -> Callable:
        for option in reversed(jira_options):
            f = option(f)

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            server = kwargs.pop("server")
            auth = kwargs.pop("auth")
            kwargs[name] = JiraWrapper(server=server, auth=auth)
            result = f(*args, **kwargs)
            return result

        return update_wrapper(wrapper, f)

    return decorator
