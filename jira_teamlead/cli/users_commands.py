import click

from jira_teamlead.cli.config_options import add_config_option, skip_config_option
from jira_teamlead.cli.jira_options import add_jira_options
from jira_teamlead.jira_wrapper import JiraWrapper


@click.command()
@add_config_option
@add_jira_options("jira")
@skip_config_option
@click.option("-p", "--project", required=True, type=str, help="Ключ проекта")
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
