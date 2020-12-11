import configparser
from pathlib import Path
from typing import Callable, Optional

import click

DEFAULT_CONFIG_FILENAME = ".jtl.cfg"
JTL_CONFIG_SECTION_PREFIX = "jtl"
JIRA_CONFIG_SECTION = "jtl.jira"
CREATE_ISSUE_CONFIG_SECTION = "jtl.create-issue"
CONFIG_CLICK_CTX_PARAM = "config"


class Config:
    SECTION_PREFIX = "jtl"
    DEFAULT_FILENAME = ".jtl.cfg"

    path: Path

    def __init__(self, path: Optional[Path] = None) -> None:
        if path is None:
            path = self._get_local_path()

        self.path = path
        self._config = configparser.ConfigParser()
        self._config.read(self.path)

    def _get_local_path(self) -> Path:
        config_path = Path().absolute() / self.DEFAULT_FILENAME
        return config_path

    def get_full_section_name(self, section: str) -> str:
        return "{0}.{1}".format(self.SECTION_PREFIX, section)

    def get(self, section: str, option: str) -> Optional[str]:
        full_section_name = self.get_full_section_name(section)
        config_section = self._config[full_section_name]
        value = config_section.get(option)
        return value


# def get_configuration(config_file: Path) -> configparser.ConfigParser:
#     config = configparser.ConfigParser()
#     config.read(config_file)
#     return config


# def get_full_section_name(section: str) -> str:
#     return "{0}.{1}".format(JTL_CONFIG_SECTION_PREFIX, section)


def bad_parameter_for_config(
    ex: click.BadParameter,
    config_path: Path,
    section: str,
    option: str,
) -> click.BadParameter:
    """Подмена исключения для параметра, заполненного из конфига.

    Заменяет название опций CLI на название параметра конфига и путь к файлу.
    """
    param_hint = "[{0}].{1} (from {2})".format(section, option, config_path)
    new_ex = click.BadParameter(
        message=ex.message,
        ctx=ex.ctx,
        param=ex.param,
        param_hint=param_hint,
    )
    return new_ex


# def get_config_path() -> Path:
#     config_path = Path().absolute() / DEFAULT_CONFIG_FILENAME
#     return config_path


def get_appropriate_config_path(ctx: click.Context) -> configparser.ConfigParser:
    """Получение подходящего конфига.

    Конфиг из параметров (из ctx)
    Локальный конфиг (.jtl.cfg)
    Глобальный конфиг (~/.jtl.cfg)
    """


# def get_from_config(section: str, name: str) -> Optional[str]:
#     config_path = get_config_path()
#     config = get_configuration(config_path)
#     full_section_name = get_full_section_name(section)
#     config_section = config[full_section_name]
#     value = config_section.get(name)

# return value


def try_get_from_config(
    callback: Callable, section: str, option: str, required: bool = False
) -> Callable:
    """Извлечение значения из конфига, если не была передана опция CLI."""

    def wrapped(
        ctx: click.Context, param: click.Parameter, value: str
    ) -> Optional[str]:
        if value is not None:  # filled cli
            return callback(ctx=ctx, param=param, value=value)
        else:  # empty cli
            config = Config()
            raw_config_value = config.get(section=section, option=option)
            if raw_config_value is None:  # empty cli, empty config
                if required:  # empty cli, empty config, required=True
                    raise click.MissingParameter(ctx=ctx, param=param)
                else:  # empty cli, empty config, required=False
                    return None
            try:  # empty cli, filled config
                value_from_config = callback(
                    ctx=ctx, param=param, value=raw_config_value
                )
            except click.BadParameter as ex:  # empty cli, incorrect config
                raise bad_parameter_for_config(
                    ex,
                    config_path=config.path,
                    section=config.get_full_section_name(section),
                    option=option,
                )
            else:  # empty cli, correct config
                return value_from_config

    return wrapped
