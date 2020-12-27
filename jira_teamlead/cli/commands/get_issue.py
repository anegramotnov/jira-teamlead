import click
import yaml

from jira_teamlead.cli.exceptions import raise_jira_response_error
from jira_teamlead.cli.options import constants
from jira_teamlead.cli.options.config import add_config_option, skip_config_option
from jira_teamlead.cli.options.jira import add_jira_options
from jira_teamlead.jira_wrapper import JiraErrorWrapper, JiraWrapper


@click.command()
@add_config_option
@add_jira_options(constants.JIRA_PARAM)
@skip_config_option
@click.argument("issue_id", type=str, required=True)
@click.pass_context
def get_issue(
    ctx: click.Context,
    jira: JiraWrapper,
    issue_id: str,
) -> None:
    """Получить все доступные поля задачи в формате YAML."""
    try:
        issue = jira.get_issue(issue_id=issue_id)
    except JiraErrorWrapper as e:
        raise_jira_response_error(jira_error_wrapper=e, ctx=ctx)

    fields = issue.raw["fields"]

    yaml_string = yaml.dump(fields, allow_unicode=True)

    click.echo(yaml_string)
