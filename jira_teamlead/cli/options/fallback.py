from typing import Any, Optional, Tuple

import click

from jira_teamlead.cli.options import constants as c
from jira_teamlead.cli.options.template import get_from_template
from jira_teamlead.config import Config


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

    def get_param_hint(self) -> Optional[str]:
        if (
            isinstance(self, ConfigFallbackMixin)
            and self.config_parameter is not None
            and self.from_config
            and self.config is not None
        ):
            hint = "'{0}.{1}' (from {2})".format(
                self.config.get_full_section_name(self.config_parameter[0]),
                self.config_parameter[1],
                self.config.path,
            )
            return hint
        else:
            return None


class TemplateFallbackMixin(click.Option):
    template_query: Optional[str] = None
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
        template = ctx.params.get(c.TEMPLATE_PARAM)
        if template is None:
            return None
        value = get_from_template(query=self.template_query, template=template)
        if value is not None:
            self.from_template = True
        return value

    # def get_param_hint(self) -> Optional[str]:
    #     raise NotImplementedError


class FallbackOption(ConfigFallbackMixin, TemplateFallbackMixin):
    fallback_required: bool = False

    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.fallback_required = kwargs.pop("required")

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

    def handle_parse_result(self, ctx: click.Context, opts: dict, args: list) -> Any:
        try:
            return super().handle_parse_result(ctx, opts, args)
        except click.BadParameter as e:
            param_hint = self.get_param_hint()
            if param_hint is not None:
                e.param_hint = param_hint
            raise

    def full_process_value(self, ctx: click.Context, value: Any) -> Any:
        value = super().full_process_value(ctx, value)
        if self.fallback_required and self.value_is_missing(value):
            raise click.MissingParameter(ctx=ctx, param=self)
        return value
