from functools import update_wrapper
from typing import Any, Callable, Dict, List

import click

from jira_teamlead.cli.options import constants as c
from jira_teamlead.cli.options.config import ConfigOption, ConfigValue
from jira_teamlead.cli.options.jira import parse_server_option
from jira_teamlead.cli.options.no_default_flag import NoDefaultFlagOption
from jira_teamlead.config import Config, get_global_config_path, get_local_config_path


class NoDefaultConfigOption(NoDefaultFlagOption, ConfigOption):
    pass


def add_config_options(prompt: bool = True) -> Callable:
    config_options = [
        click.option(
            c.LOCAL_CONFIG_FULL,
            cls=NoDefaultFlagOption,
            required=True,
            is_flag=True,
            help=c.LOCAL_CONFIG_HELP,
        ),
        click.option(
            c.SERVER_SHORT,
            c.SERVER_FULL,
            c.SERVER_PARAM,
            cls=ConfigOption,
            config_parameter=c.SERVER_CONFIG,
            prompt=c.SERVER_HELP if prompt else False,
            callback=parse_server_option,
            help=c.SERVER_HELP,
        ),
        click.option(
            c.LOGIN_SHORT,
            c.LOGIN_FULL,
            c.LOGIN_PARAM,
            cls=ConfigOption,
            config_parameter=c.LOGIN_CONFIG,
            prompt=c.LOGIN_HELP if prompt else False,
            help=c.LOGIN_HELP,
        ),
        click.option(
            c.PASSWORD_SHORT,
            c.PASSWORD_FULL,
            c.PASSWORD_PARAM,
            cls=ConfigOption,
            config_parameter=c.PASSWORD_CONFIG,
            prompt=c.PASSWORD_HELP + " (можно пропустить)" if prompt else False,
            hide_input=True,
            show_default=False,
            show_choices=False,
            default="",
            help=c.PASSWORD_HELP,
        ),
        click.option(
            c.PROJECT_SHORT,
            c.PROJECT_FULL,
            c.PROJECT_PARAM,
            cls=ConfigOption,
            config_parameter=c.PROJECT_CONFIG,
            prompt=c.PROJECT_CONFIG_HELP if prompt else False,
            help=c.PROJECT_CONFIG_HELP,
        ),
        click.option(
            c.TEMPLATE_SHORT,
            c.TEMPLATE_FULL,
            c.TEMPLATE_PARAM,
            cls=ConfigOption,
            type=click.Path(),
            required=False,
            config_parameter=c.TEMPLATE_CONFIG,
            help=c.TEMPLATE_HELP,
        ),
        click.option(
            c.OPEN_LINK_FULL,
            c.OPEN_LINK_PARAM,
            config_parameter=c.OPEN_LINK_CONFIG,
            is_flag=True,
            cls=ConfigOption if prompt else NoDefaultConfigOption,
            prompt=c.OPEN_LINK_CONFIG_HELP + "?" if prompt else False,
            default=True if prompt else None,
            show_default=False,
            help=c.OPEN_LINK_CONFIG_HELP,
        ),
    ]

    def decorator(f: Callable) -> Callable:
        for option in reversed(config_options):
            f = option(f)

        def wrapper(**kwargs: Any) -> Any:
            f(**kwargs)

        return update_wrapper(wrapper, f)

    return decorator


@click.group(name="config")
def config_group() -> None:
    """Группа команд управления конфигурацией."""


@config_group.command(name="init")
@add_config_options(prompt=True)
def config_init(
    local: bool, config_values: List[ConfigValue], **kwargs: Dict[str, Any]
) -> None:
    """Создать (перезаписать) конфигурационный файл."""
    if local:
        config_path = get_local_config_path()
    else:
        config_path = get_global_config_path()
    config = Config(path=config_path)

    for value in config_values:
        config.set(**value._asdict())

    config.save()


@config_group.command(name="set")
@add_config_options(prompt=False)
def config_set(
    local: bool, config_values: List[ConfigValue], **kwargs: Dict[str, Any]
) -> None:
    """Изменить конфигурационный параметр(ы) в конфигурационном файле."""
    if local:
        config_path = get_local_config_path()
    else:
        config_path = get_global_config_path()
    config = Config(path=config_path)

    for value in config_values:
        config.set(**value._asdict())

    config.save()
