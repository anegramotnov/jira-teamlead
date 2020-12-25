import click
import yaml

from jira_teamlead.cli.options import constants
from jira_teamlead.cli.options.config import add_config_option, skip_config_option
from jira_teamlead.cli.options.jira import add_jira_options
from jira_teamlead.jira_wrapper import JiraWrapper


@click.command()
@add_config_option
@add_jira_options(constants.JIRA_PARAM)
@skip_config_option
@click.argument("issue_id", type=str, required=True)
def get_issue(
    jira: JiraWrapper,
    issue_id: str,
) -> None:
    """Получить все доступные поля задачи в формате YAML."""
    issue = jira.get_issue(issue_id=issue_id)

    fields = issue.raw["fields"]

    yaml_string = yaml.dump(fields, allow_unicode=True)

    click.echo(yaml_string)
