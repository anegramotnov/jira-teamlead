import click

from jira_teamlead.cli.autocompletion import (
    autocompletion_with_jira,
    project_autocompletion,
)
from jira_teamlead.cli.options import constants as c
from jira_teamlead.cli.options.config import add_config_option, skip_config_option
from jira_teamlead.cli.options.fallback import FallbackOption
from jira_teamlead.cli.options.jira import add_jira_options
from jira_teamlead.jira_wrapper import Jira


@click.command()
@add_config_option
@add_jira_options(c.JIRA_PARAM)
@skip_config_option
@click.option(
    c.PROJECT_SHORT,
    c.PROJECT_FULL,
    c.PROJECT_PARAM,
    cls=FallbackOption,
    type=str,
    required=True,
    autocompletion=autocompletion_with_jira(project_autocompletion),
    prompt=c.PROJECT_HELP,
    help=c.PROJECT_HELP,
    config_parameter=c.PROJECT_CONFIG,
)
@click.argument("search_string", type=str, required=False)
def search_users(
    jira: Jira,
    project: str,
    search_string: str,
) -> None:
    """Показать пользовательские логины, доступные для поля assignee.

    Доступна фильтрация по SEARCH_STRING.
    """
    users = jira.search_users(project=project, search_string=search_string)

    for user in users:
        click.echo(f"{user.name} ({user.displayName}, {user.emailAddress})")
