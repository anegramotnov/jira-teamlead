import click

from jira_teamlead.cli.autocompletion import (
    autocompletion_with_jira,
    project_autocompletion,
)
from jira_teamlead.cli.options import constants
from jira_teamlead.cli.options.config import (
    add_config_option,
    from_config_fallback,
    skip_config_option,
)
from jira_teamlead.cli.options.fallback import FallbackOption
from jira_teamlead.cli.options.jira import add_jira_options
from jira_teamlead.jira_wrapper import JiraWrapper


@click.command()
@add_config_option
@add_jira_options(constants.JIRA_PARAM)
@skip_config_option
@click.option(
    constants.PROJECT_SHORT,
    constants.PROJECT_FULL,
    constants.PROJECT_PARAM,
    cls=FallbackOption,
    type=str,
    required=True,
    autocompletion=autocompletion_with_jira(project_autocompletion),
    prompt=True,
    help=constants.PROJECT_HELP,
    fallback=from_config_fallback(*constants.PROJECT_CONFIG),
)
@click.argument("search_string", type=str, required=False)
def search_users(
    jira: JiraWrapper,
    project: str,
    search_string: str,
) -> None:
    """Показать логины, доступные для поля assignee.

    Доступна фильтрация по SEARCH_STRING.
    """
    users = jira.search_users(project=project, search_string=search_string)

    for user in users:
        click.echo(f"{user.name} ({user.displayName}, {user.emailAddress})")
