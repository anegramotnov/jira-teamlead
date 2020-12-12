from functools import update_wrapper
from pathlib import Path
from typing import Any, Callable, Optional

import click

from jira_teamlead.cli.config import Config


def parse_config_option(
    ctx: click.Context, param: click.Parameter, value: Optional[str]
) -> Optional[Config]:
    if value:
        path = Path(value)
        config = Config(path)
        return config
    else:
        return None


def add_config_option(f: Callable) -> Callable:
    """Добавить опцию конфига."""
    config_option = click.option(
        "-cfg",
        "--config",
        type=click.Path(),
        required=False,
        callback=parse_config_option,
        help="Путь к файлу конфигурации",
    )
    f = config_option(f)
    return f


def skip_config_option(f: Callable) -> Callable:
    """Убрать опцию конфига из аргументов команды.

    Декоратор должен следовать после add_config_option и других опций, которые
    полагаются на наличие параметра config.
    """

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        kwargs.pop("config")
        result = f(*args, **kwargs)
        return result

    return update_wrapper(wrapper, f)