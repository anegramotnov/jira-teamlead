import io
from typing import Any, Callable, Optional

import click
import yaml

from jira_teamlead.cli.fallback_options import FallbackOption

TEMPLATE_CLICK_PARAM = "template"


def parse_yaml_option(
    ctx: click.Context, param: click.Parameter, value: Optional[io.TextIOWrapper]
) -> Optional[dict]:
    if value is not None:
        template = yaml.safe_load(value)
        return template
    else:
        return None


def _get_from_template(query: str, template: dict) -> Optional[str]:
    parts = query.split(".")
    if not parts:
        return None
    value: Any = template
    for part in parts:
        value = value.get(part)
        if value is None:
            return None
    return value


def from_template_fallback(query: str) -> Callable:
    def fallback(ctx: click.Context, param: FallbackOption) -> Optional[str]:
        template = ctx.params[TEMPLATE_CLICK_PARAM]
        if template is None:
            return None
        value = _get_from_template(query=query, template=template)
        return value

    return fallback
