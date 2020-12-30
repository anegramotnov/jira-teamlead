import webbrowser
from typing import TYPE_CHECKING, Optional

import click

from jira_teamlead.cli.autocompletion import (
    assignee_autocompletion,
    autocompletion_with_jira,
    issue_type_autocompletion,
    project_autocompletion,
)
from jira_teamlead.cli.exceptions import raise_jira_response_error
from jira_teamlead.cli.options import constants as c
from jira_teamlead.cli.options.config import add_config_option, skip_config_option
from jira_teamlead.cli.options.fallback import FallbackOption
from jira_teamlead.cli.options.jira import add_jira_options
from jira_teamlead.cli.options.template import IssueTemplateType
from jira_teamlead.jira_wrapper import Jira, JiraError

if TYPE_CHECKING:
    from jira_teamlead.issue_template import IssueTemplate


@click.command()
@add_config_option
@add_jira_options(c.JIRA_PARAM)
@click.option(
    c.TEMPLATE_SHORT,
    c.TEMPLATE_FULL,
    c.TEMPLATE_PARAM,
    cls=FallbackOption,
    type=IssueTemplateType(),
    required=False,
    help=c.TEMPLATE_HELP,
    config_parameter=c.TEMPLATE_CONFIG,
)
@click.option(
    c.PROJECT_SHORT,
    c.PROJECT_FULL,
    c.PROJECT_PARAM,
    cls=FallbackOption,
    type=str,
    required=True,
    autocompletion=autocompletion_with_jira(project_autocompletion),
    prompt=c.PROJECT_CONFIG_HELP,
    help=c.PROJECT_HELP,
    template_query=c.PROJECT_TEMPLATE_QUERY,
    config_parameter=c.PROJECT_CONFIG,
)
@skip_config_option
@click.option(
    c.ISSUE_TYPE_SHORT,
    c.ISSUE_TYPE_FULL,
    c.ISSUE_TYPE_PARAM,
    cls=FallbackOption,
    type=str,
    required=True,
    autocompletion=autocompletion_with_jira(issue_type_autocompletion),
    prompt=c.ISSUE_TYPE_HELP,
    help=c.ISSUE_TYPE_HELP,
    template_query=c.ISSUE_TYPE_TEMPLATE_QUERY,
)
@click.option(
    c.ASSIGNEE_SHORT,
    c.ASSIGNEE_FULL,
    c.ASSIGNEE_PARAM,
    type=str,
    required=False,
    autocompletion=autocompletion_with_jira(assignee_autocompletion),
    help=c.ASSIGNEE_HELP,
)
@click.option(
    c.SUMMARY_SHORT,
    c.SUMMARY_FULL,
    c.SUMMARY_PARAM,
    cls=FallbackOption,
    type=str,
    required=True,
    prompt=c.SUMMARY_HELP,
    help=c.SUMMARY_HELP,
    template_query=c.SUMMARY_TEMPLATE_QUERY,
)
@click.option(
    c.OPEN_LINK_FULL,
    c.OPEN_LINK_PARAM,
    cls=FallbackOption,
    required=True,
    default=True,
    is_flag=True,
    help=c.OPEN_LINK_HELP,
    config_parameter=c.OPEN_LINK_CONFIG,
)
@click.pass_context
def create_issue(
    ctx: click.Context,
    jira: Jira,
    issue_template: Optional["IssueTemplate"],
    project: str,
    issue_type: str,
    assignee: Optional[str],
    summary: str,
    open_in_browser: bool,
) -> None:
    """Создание задачи."""
    fields = {
        "project": {
            "key": project,
        },
        "issuetype": {
            "name": issue_type,
        },
        "summary": summary,
    }

    if assignee is not None:
        assignee_field = {"assignee": {"name": assignee}}
        fields.update(assignee_field)

    if issue_template is not None:
        fields = issue_template.apply_template(issue_fields=fields)

    try:
        created_issue = jira.create_issue(fields=fields)
    except JiraError as e:
        raise_jira_response_error(jira_error_wrapper=e, ctx=ctx)
    else:
        click.echo(f"Created issue: {created_issue.link}")
        if open_in_browser:
            webbrowser.open_new_tab(created_issue.link)
