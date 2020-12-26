import configparser
from pathlib import Path
from typing import List, Optional, Union

JIRA_SECTION = "jira"
DEFAULTS_SECTION = "defaults"
DEFAULTS_CREATE_ISSUE_SECTION = "defaults.create-issue"
DEFAULT_CONFIG_FILENAME = ".jtl.cfg"


def get_local_config_path() -> Path:
    config_path = Path().absolute() / DEFAULT_CONFIG_FILENAME
    return config_path


def get_global_config_path() -> Path:
    config_path = Path().home() / DEFAULT_CONFIG_FILENAME
    return config_path


def get_suitable_config(custom_path: Optional[Union[Path, str]]) -> Optional["Config"]:
    paths: List[Union[Path, str]] = [get_global_config_path(), get_local_config_path()]
    if custom_path is not None:
        paths.append(custom_path)

    for path in reversed(paths):
        config = Config(path)
        if config.exists:
            return config
        else:
            return None
    else:
        return None


class Config:
    SECTION_PREFIX = "jtl"
    DEFAULT_FILENAME = ".jtl.cfg"

    path: Path
    _exists: bool = False

    def __init__(self, path: Union[Path, str]) -> None:
        if isinstance(path, str):
            path = Path(path)

        self._config = configparser.ConfigParser()
        configs = self._config.read(path)
        if configs:
            self._exists = True
        self.path = path

    @property
    def exists(self) -> bool:
        return self._exists

    def get_full_section_name(self, section: str) -> str:
        return "{0}.{1}".format(self.SECTION_PREFIX, section)

    def get(self, section: str, option: str) -> Optional[str]:
        full_section_name = self.get_full_section_name(section)

        try:
            value = self._config.get(section=full_section_name, option=option)
            return value
        except configparser.Error:
            return None

    def set(self, section: str, option: str, value: Union[str, bool]) -> None:
        if isinstance(value, bool):
            value = str(value).lower()

        full_section_name = self.get_full_section_name(section)

        self._config.setdefault(full_section_name, {})
        self._config[full_section_name][option] = value

    def save(self) -> None:
        with self.path.open("w") as config_file:
            self._config.write(config_file)
