from functools import update_wrapper
from typing import Any, Callable, Optional

import click

from jira_teamlead.cli.fallback_options import FallbackOption
from jira_teamlead.config import Config

CONFIG_CLICK_PARAM = "config"


def parse_config_option(
    ctx: click.Context, param: click.Parameter, value: Optional[str]
) -> Optional[Config]:
    config = Config(custom_path=value)
    return config


def add_config_option(f: Callable) -> Callable:
    """Добавить опцию конфига."""
    config_option = click.option(
        "-jc",
        "--config",
        CONFIG_CLICK_PARAM,
        type=click.Path(exists=True, dir_okay=False),
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
        kwargs.pop(CONFIG_CLICK_PARAM)
        result = f(*args, **kwargs)
        return result

    return update_wrapper(wrapper, f)


def from_config_fallback(section: str, option: str) -> Callable:
    def fallback(ctx: click.Context, param: FallbackOption) -> Optional[str]:
        config: Config = ctx.params[CONFIG_CLICK_PARAM]
        value = config.get(section=section, option=option)
        if value is not None:
            # for override e.param_hint
            param.fallback_hint = "'{0}.{1}' (from {2})".format(
                config.get_full_section_name(section), option, config.path
            )
        return value

    return fallback
