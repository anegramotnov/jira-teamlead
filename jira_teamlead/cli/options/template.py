import io
from typing import Any, Optional

import click
import yaml


def parse_yaml_option(
    ctx: click.Context, param: click.Parameter, value: Optional[io.TextIOWrapper]
) -> Optional[dict]:
    if value is not None:
        template = yaml.safe_load(value)
        return template
    else:
        return None


def get_from_template(query: str, template: dict) -> Optional[str]:
    parts = query.split(".")
    value: Any = template
    for part in parts:
        value = value.get(part)
        if value is None:
            return None
    return value
