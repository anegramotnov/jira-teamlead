import webbrowser
from typing import Optional

import click

from jira_teamlead.cli.autocompletion import (
    assignee_autocompletion,
    autocompletion_with_jira,
    issue_type_autocompletion,
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
from jira_teamlead.cli.options.template import from_template_fallback, parse_yaml_option
from jira_teamlead.jira_wrapper import JiraWrapper


@click.command()
@add_config_option
@add_jira_options(constants.JIRA_PARAM)
@click.option(
    constants.TEMPLATE_SHORT,
    constants.TEMPLATE_FULL,
    constants.TEMPLATE_PARAM,
    cls=FallbackOption,
    type=click.File("r", encoding="utf-8"),
    required=False,
    callback=parse_yaml_option,
    help=constants.TEMPLATE_HELP,
    fallback=from_config_fallback(*constants.TEMPLATE_CONFIG),
)
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
    fallback=[
        from_template_fallback(constants.PROJECT_TEMPLATE_QUERY),
        from_config_fallback(*constants.PROJECT_CONFIG),
    ],
)
@skip_config_option
@click.option(
    constants.ISSUE_TYPE_SHORT,
    constants.ISSUE_TYPE_FULL,
    constants.ISSUE_TYPE_PARAM,
    cls=FallbackOption,
    type=str,
    required=True,
    autocompletion=autocompletion_with_jira(issue_type_autocompletion),
    prompt=True,
    help=constants.ISSUE_TYPE_HELP,
    fallback=from_template_fallback(constants.ISSUE_TYPE_TEMPLATE_QUERY),
)
@click.option(
    constants.ASSIGNEE_SHORT,
    constants.ASSIGNEE_FULL,
    constants.ASSIGNEE_PARAM,
    type=str,
    required=False,
    autocompletion=autocompletion_with_jira(assignee_autocompletion),
    help=constants.ASSIGNEE_HELP,
)
@click.option(
    constants.SUMMARY_SHORT,
    constants.SUMMARY_FULL,
    constants.SUMMARY_PARAM,
    type=str,
    required=True,
    prompt=True,
    help=constants.SUMMARY_HELP,
)
@click.option(
    constants.OPEN_LINK_FULL,
    constants.OPEN_LINK_PARAM,
    cls=FallbackOption,
    required=True,
    default=True,
    is_flag=True,
    help=constants.OPEN_LINK_HELP,
    fallback=from_config_fallback(*constants.OPEN_LINK_CONFIG),
)
def create_issue(
    jira: JiraWrapper,
    issue_template: Optional[dict],
    project: str,
    issue_type: str,
    assignee: Optional[str],
    summary: str,
    open_in_browser: bool,
) -> None:
    """Создание Issue."""
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

    created_issue = jira.create_issue(fields=fields, template=issue_template)

    click.echo(f"Created issue: {created_issue.link}")
    if open_in_browser:
        webbrowser.open_new_tab(created_issue.link)
