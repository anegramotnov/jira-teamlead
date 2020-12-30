import webbrowser
from typing import List, Optional

import click

from jira_teamlead.cli.options import constants as c
from jira_teamlead.cli.options.config import add_config_option, skip_config_option
from jira_teamlead.cli.options.fallback import FallbackOption
from jira_teamlead.cli.options.jira import add_jira_options
from jira_teamlead.cli.options.template import IssueTemplateType, YamlType
from jira_teamlead.issue_template import IssueTemplate
from jira_teamlead.jira_wrapper import Jira, SuperIssue
from jira_teamlead.type_aliases import IssueFieldsT


@click.command()
@add_config_option
@add_jira_options(c.JIRA_PARAM)
@skip_config_option
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
    c.OPEN_LINK_FULL,
    c.OPEN_LINK_PARAM,
    cls=FallbackOption,
    required=True,
    default=True,
    is_flag=True,
    help=c.OPEN_LINK_HELP,
    config_parameter=c.OPEN_LINK_CONFIG,
)
@click.argument(
    "issue_set",
    type=YamlType(),
)
def create_issue_set(
    jira: Jira,
    issue_template: Optional[IssueTemplate],
    open_in_browser: bool,
    issue_set: List[IssueFieldsT],
) -> None:
    """Создание набора Issue из yaml-файла ISSUE_SET_FILE"""
    if issue_template is not None:
        for index, issue_fields in enumerate(issue_set):
            issue_set[index] = issue_template.apply_template(issue_fields=issue_fields)

    issues = jira.create_issue_set(
        issue_set=issue_set,
    )

    for issue in issues:
        if isinstance(issue, SuperIssue):
            click.echo(f"Created super-issue: {jira.server}/browse/{issue.key}")
            for sub_issue in issue.sub_issues:
                click.echo(
                    f"    Created sub-issue: {jira.server}/browse/{sub_issue.key}"
                )
                if open_in_browser:
                    webbrowser.open_new_tab(sub_issue.link)

        else:
            click.echo(f"Created issue: {jira.server}/browse/{issue.key}")
            if open_in_browser:
                webbrowser.open_new_tab(issue.link)
