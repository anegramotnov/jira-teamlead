import configparser
from pathlib import Path
from typing import Callable, Optional, Union

import click

CONFIG_CLICK_PARAM = "config"


class Config:
    SECTION_PREFIX = "jtl"
    DEFAULT_FILENAME = ".jtl.cfg"

    path: Optional[Path] = None

    def __init__(self, custom_path: Optional[Union[Path, str]]) -> None:
        self._config = configparser.ConfigParser()
        if isinstance(custom_path, str):
            custom_path = Path(custom_path)

        self._read_config(custom_path=custom_path)

    def _read_config(self, custom_path: Optional[Path]) -> None:
        paths = [self._get_global_path(), self._get_local_path()]
        if custom_path is not None:
            paths.append(custom_path)

        for path in reversed(paths):
            config_file = self._config.read(path)
            if config_file:
                self.path = path
                break

    def _get_local_path(self) -> Path:
        config_path = Path().absolute() / self.DEFAULT_FILENAME
        return config_path

    def _get_global_path(self) -> Path:
        config_path = Path().home() / self.DEFAULT_FILENAME
        return config_path

    def get_full_section_name(self, section: str) -> str:
        return "{0}.{1}".format(self.SECTION_PREFIX, section)

    def get(self, section: str, option: str) -> Optional[str]:
        full_section_name = self.get_full_section_name(section)

        if self.path is None:
            return None
        try:
            value = self._config.get(section=full_section_name, option=option)
            return value
        except configparser.Error:
            return None


def bad_parameter_for_config(
    ex: click.BadParameter,
    config_path: Path,
    section: str,
    option: str,
) -> click.BadParameter:
    """Подмена исключения для параметра, заполненного из конфига.

    Заменяет название опций CLI на название параметра конфига и путь к файлу.
    """
    param_hint = "'{0}.{1}' (from {2})".format(section, option, config_path)
    new_ex = click.BadParameter(
        message=ex.message,
        ctx=ex.ctx,
        param=ex.param,
        param_hint=param_hint,
    )
    return new_ex


def try_get_from_config(
    custom_parser: Callable, section: str, option: str, required: bool = False
) -> Callable:
    """Извлечение значения из конфига, если не была передана опция CLI."""

    def wrapped(
        ctx: click.Context, param: click.Parameter, value: str
    ) -> Optional[str]:
        if value is not None:  # filled cli
            return custom_parser(ctx=ctx, param=param, value=value)
        else:  # empty cli
            config = ctx.params[CONFIG_CLICK_PARAM]
            raw_config_value = config.get(section=section, option=option)
            if raw_config_value is None:  # empty cli, empty config
                if required:  # empty cli, empty config, required=True
                    raise click.MissingParameter(ctx=ctx, param=param)
                else:  # empty cli, empty config, required=False
                    return None
            try:  # empty cli, filled config
                converted_value = param.full_process_value(ctx, raw_config_value)
                parsed_value = custom_parser(
                    ctx=ctx, param=param, value=converted_value
                )
            except click.BadParameter as ex:  # empty cli, incorrect config
                raise bad_parameter_for_config(
                    ex,
                    config_path=config.path,
                    section=config.get_full_section_name(section),
                    option=option,
                )
            else:  # empty cli, correct config
                return parsed_value

    return wrapped
