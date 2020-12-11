from typing import Tuple
from urllib.parse import urlparse

import click


def parse_auth_option(
    ctx: click.Context, param: click.Parameter, value: str
) -> Tuple[str, str]:
    """Валидация параметра --user."""
    try:
        value.encode("ascii")
    except UnicodeEncodeError:
        raise click.BadParameter("ожидаются символы ASCII")

    splitted_parts = value.split(":")
    if len(splitted_parts) != 2 or not all(splitted_parts):
        raise click.BadParameter("ожидается формат 'login:password'")

    login, password = splitted_parts

    return login, password


def parse_server_option(ctx: click.Context, param: click.Parameter, value: str) -> str:
    """Валидация и преобразование параметра --jira-host."""
    url = urlparse(value)

    if not all([url.scheme, url.netloc]):
        raise click.BadParameter("ожидается формат 'http[s]://jira.host.net'")

    return f"{url.scheme}://{url.netloc}"
