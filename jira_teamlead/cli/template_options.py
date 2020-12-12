import io
from typing import Any, Optional

import click
import yaml

TEMPLATE_CLICK_PARAM = "template"


def parse_yaml_option(
    ctx: click.Context, param: click.Parameter, value: Optional[io.TextIOWrapper]
) -> Optional[dict]:
    if value is not None:
        template = yaml.safe_load(value)
        return template
    else:
        return None


class IssueTemplateOption(click.Option):
    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        template_var = kwargs.pop("template_var")
        super().__init__(*args, **kwargs)
        self.template_var = template_var

    def value_from_template(self, ctx: click.Context) -> Optional[str]:
        if self.template_var is None:
            return None
        template = ctx.params[TEMPLATE_CLICK_PARAM]
        if template is None:
            return None
        parts = self.template_var.split(".")
        value = template
        for part in parts:
            value = value.get(part)
            if value is None:
                return None
        return value

    def consume_value(self, ctx: click.Context, opts: dict) -> Any:
        value = opts.get(self.name)
        if value is None:
            value = self.value_from_envvar(ctx)
        if value is None:
            value = self.value_from_template(ctx)
        if value is None:
            value = ctx.lookup_default(self.name)
        return value
