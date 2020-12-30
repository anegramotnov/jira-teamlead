from typing import Any, Optional, Tuple

import click

from jira_teamlead.cli.options import constants as c
from jira_teamlead.config import Config
from jira_teamlead.issue_template import IssueTemplate


class ConfigFallbackMixin(click.Option):
    config_parameter: Optional[Tuple[str, str]] = None
    config: Optional[Config] = None
    from_config: bool = False

    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        if c.CONFIG_PARAMETER_ATTRIBUTE in kwargs:
            self.config_parameter = kwargs.pop(c.CONFIG_PARAMETER_ATTRIBUTE)

        # TODO: Возможно, есть смысл извлекать конфиг прямо в __init__

        super().__init__(*args, **kwargs)

    def value_from_config(self, ctx: click.Context) -> Optional[str]:
        if self.config_parameter is None:
            return None
        config: Optional[Config] = ctx.params.get(c.CONFIG_FILE_PARAM)
        if config is None:
            return None
        value = config.get(*self.config_parameter)
        if value is not None:
            self.config = config
            self.from_config = True
        return value


class TemplateFallbackMixin(click.Option):
    template_query: Optional[str] = None
    template: Optional[IssueTemplate] = None
    from_template: bool = False

    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        if c.TEMPLATE_QUERY_ATTRIBUTE in kwargs:
            self.template_query = kwargs.pop(c.TEMPLATE_QUERY_ATTRIBUTE)

        super().__init__(*args, **kwargs)

    def value_from_template(self, ctx: click.Context) -> Optional[str]:
        if self.template_query is None:
            return None
        template: Optional[IssueTemplate] = ctx.params.get(c.TEMPLATE_PARAM)
        if template is None:
            return None

        value = template.get(query=self.template_query)

        if value is not None:
            self.template = template
            self.from_template = True
        return value


class FallbackOption(ConfigFallbackMixin, TemplateFallbackMixin):
    fallback_required: bool = False

    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.fallback_required = kwargs.pop("required", False)

        super().__init__(*args, **kwargs)

    def consume_value(self, ctx: click.Context, opts: dict) -> Any:
        value = opts.get(self.name)
        if value is None:
            value = self.value_from_envvar(ctx)
        if value is None and self.template_query:
            value = self.value_from_template(ctx)
        if value is None and self.config_parameter:
            value = self.value_from_config(ctx)
        if value is None:
            value = ctx.lookup_default(self.name)
        return value

    def full_process_value(self, ctx: click.Context, value: Any) -> Any:
        value = super().full_process_value(ctx, value)
        if self.fallback_required and self.value_is_missing(value):
            raise click.MissingParameter(ctx=ctx, param=self)
        return value

    def get_error_hint(self, ctx: click.Context) -> str:
        value = ctx.params[self.name]

        if self.template_query and self.from_template and self.template is not None:
            return "'{0}: {1}' (from {2})".format(
                self.template_query, value, self.template.path
            )
        if (
            self.config_parameter is not None
            and self.from_config
            and self.config is not None
        ):
            hint = "'{0}.{1} = {2}' (from {3})".format(
                self.config.get_full_section_name(self.config_parameter[0]),
                self.config_parameter[1],
                value,
                self.config.path,
            )
            return hint
        return super().get_error_hint(ctx)
