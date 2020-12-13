import configparser
from pathlib import Path
from typing import Optional, Union


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
