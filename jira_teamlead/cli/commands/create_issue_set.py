import click

from jira_teamlead import jtl_fields
from jira_teamlead.cli.options import constants
from jira_teamlead.cli.options.config import add_config_option, skip_config_option
from jira_teamlead.cli.options.jira import add_jira_options
from jira_teamlead.cli.options.template import parse_yaml_option
from jira_teamlead.jira_wrapper import JiraWrapper, SuperIssue


@click.command()
@add_config_option
@add_jira_options(constants.JIRA_PARAM)
@skip_config_option
@click.argument(
    "issue_set", type=click.File("r", encoding="utf-8"), callback=parse_yaml_option
)
def create_issue_set(jira: JiraWrapper, issue_set: dict) -> None:
    """Создание набора Issue из yaml-файла ISSUE_SET_FILE."""
    issues = issue_set[jtl_fields.ISSUE_SET_FIELD]
    issue_template = issue_set.get(jtl_fields.TEMPLATE_FIELD)

    issues = jira.create_issue_set(
        issues=issues,
        template=issue_template,
    )

    for issue in issues:
        if isinstance(issue, SuperIssue):
            click.echo(f"Created super-issue: {jira.server}/browse/{issue.key}")
            for sub_issue in issue.sub_issues:
                click.echo(
                    f"    Created sub-issue: {jira.server}/browse/{sub_issue.key}"
                )
        else:
            click.echo(f"Created issue: {jira.server}/browse/{issue.key}")
