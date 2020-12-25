from typing import Any, List, Optional, Tuple, Union

import click

from jira_teamlead.cli import context_settings, init_jtl, jtl
from jira_teamlead.cli.options import constants as c
from jira_teamlead.cli.options.fallback import TemplateFallbackMixin


def define_env(env: Any) -> None:
    init_jtl()

    def get_command_with_ctx(
        *command_names: str,
    ) -> Tuple[Union[click.Command, click.Group], click.Context]:
        parent_group: Union[click.Command, click.Group] = jtl
        ctx = click.Context(
            command=jtl,
            parent=None,
            info_name="jtl",
            **context_settings,  # type: ignore[arg-type]
        )

        for command_name in command_names:
            if isinstance(parent_group, click.Group):
                command: Union[click.Command, click.Group] = parent_group.commands[
                    command_name
                ]
                ctx = click.Context(
                    command=command,
                    parent=ctx,
                    info_name=command_name,
                    **context_settings,  # type: ignore[arg-type]
                )
                parent_group = command

        return command, ctx

    @env.macro
    def get_command_usage(*command_names: str) -> str:
        command, ctx = get_command_with_ctx(*command_names)
        return "$ {0} {1}".format(
            ctx.command_path, " ".join(command.collect_usage_pieces(ctx))
        )

    @env.macro
    def get_command_help(*command_names: str) -> Optional[str]:
        command, ctx = get_command_with_ctx(*command_names)
        return command.help

    @env.macro
    def get_command_params(*command_names: str) -> List[click.Parameter]:
        command, ctx = get_command_with_ctx(*command_names)
        params_excluding_help = [
            param for param in command.get_params(ctx) if not param.name == "help"
        ]

        return params_excluding_help

    @env.macro
    def get_param_opts(param: Union[click.Option, click.Argument]) -> str:
        pieces = [param.opts[0]]
        if isinstance(param, click.Argument):
            return pieces[0].upper()

        if param.is_flag and param.secondary_opts:
            pieces.append(param.secondary_opts[0])
        elif not param.is_flag:
            pieces.append(param.opts[1])
        return "/".join(pieces)

    @env.macro
    def get_param_config(param: click.Option) -> str:
        if hasattr(param, c.CONFIG_PARAMETER_ATTRIBUTE) and getattr(
            param, c.CONFIG_PARAMETER_ATTRIBUTE
        ):

            section, parameter_name = getattr(param, c.CONFIG_PARAMETER_ATTRIBUTE)
            return parameter_name
        else:
            return "-"

    @env.macro
    def get_template_query(param: TemplateFallbackMixin) -> str:
        if hasattr(param, c.TEMPLATE_QUERY_ATTRIBUTE) and getattr(
            param, c.TEMPLATE_QUERY_ATTRIBUTE
        ):
            query = getattr(param, c.TEMPLATE_QUERY_ATTRIBUTE)
            return query
        else:
            return "-"

    @env.macro
    def get_param_required(param: click.Option) -> str:
        if hasattr(param, "fallback_required") and getattr(  # noqa: B009
            param, "fallback_required"
        ):
            return "+"
        return "+" if param.required else "-"

    @env.macro
    def get_param_prompt(param: click.Option) -> str:
        return "+" if param.prompt else "-"

    env.macro(get_command_with_ctx, "get_command")

    env.variables.c = c

    env.variables.jtl = jtl
