from functools import update_wrapper
from typing import Any, Callable, List, NamedTuple, Optional, Tuple, Union

import click

from jira_teamlead.cli.options import constants
from jira_teamlead.config import Config, get_suitable_config


def parse_config_option(
    ctx: click.Context, param: click.Parameter, value: Optional[str]
) -> Optional[Config]:
    config = get_suitable_config(custom_path=value)
    return config


def add_config_option(f: Callable) -> Callable:
    """Добавить опцию конфига."""
    config_option = click.option(
        constants.CONFIG_FILE_SHORT,
        constants.CONFIG_FILE_FULL,
        constants.CONFIG_FILE_PARAM,
        type=click.Path(exists=True, dir_okay=False),
        required=False,
        callback=parse_config_option,
        help=constants.CONFIG_FILE_HELP,
    )
    f = config_option(f)
    return f


def skip_config_option(f: Callable) -> Callable:
    """Убрать опцию конфига из аргументов команды.

    Декоратор должен следовать после add_config_option и других опций, которые
    полагаются на наличие параметра config.
    """

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        kwargs.pop(constants.CONFIG_FILE_PARAM)
        result = f(*args, **kwargs)
        return result

    return update_wrapper(wrapper, f)


class ConfigValue(NamedTuple):
    section: str
    option: str
    value: Union[str, bool]


class ConfigOption(click.Option):
    config_parameter: Tuple[str, str]

    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.config_parameter = kwargs.pop(constants.CONFIG_PARAMETER_ATTRIBUTE)

        super().__init__(*args, **kwargs)

    def handle_parse_result(
        self, ctx: click.Context, opts: Any, args: Any
    ) -> Tuple[Any, List[str]]:
        value, args = super().handle_parse_result(ctx, opts, args)
        config_values = ctx.params.setdefault(constants.CONFIG_VALUES_PARAM, [])
        if value:
            config_values.append(ConfigValue(*self.config_parameter, value))

        return value, args
