from typing import List, Optional

import click
import yaml

from jira_teamlead import jtl_fields
from jira_teamlead.cli.config import try_get_from_config
from jira_teamlead.cli.config_options import add_config_option, skip_config_option
from jira_teamlead.cli.jira_options import add_jira_options, set_jira_to_params
from jira_teamlead.cli.template_options import (
    TEMPLATE_CLICK_PARAM,
    IssueTemplateOption,
    parse_yaml_option,
)
from jira_teamlead.jira_wrapper import JiraWrapper, SuperIssue


def get_assignees(ctx: click.Context, args: List[str], incomplete: str) -> List[str]:
    set_jira_to_params(ctx.params)
    jira: JiraWrapper = ctx.params["jira"]
    project: str = ctx.params["project"]
    users = jira.search_users(project=project, search_string=incomplete)
    usernames = [u.name for u in users]
    return usernames


@click.command()
@add_config_option
@add_jira_options("jira")
@click.option(
    "-tmpl",
    "--template",
    TEMPLATE_CLICK_PARAM,
    type=click.File("r", encoding="utf-8"),
    callback=try_get_from_config(
        parse_yaml_option, section="create-issue", option="issue_template"
    ),
)
@skip_config_option
@click.option(
    "-p",
    "--project",
    cls=IssueTemplateOption,
    required=True,
    type=str,
    help="Ключ проекта",
    template_var="project.key",
)
@click.option(
    "-t",
    "--type",
    "issue_type",
    cls=IssueTemplateOption,
    required=True,
    type=str,
    help="Тип Issue",
    template_var="issuetype.name",
)
@click.option(
    "-s",
    "--summary",
    cls=IssueTemplateOption,
    required=True,
    type=str,
    help="Название задачи",
    template_var="summary",
)
@click.option(
    "-a",
    "--assignee",
    cls=IssueTemplateOption,
    required=False,
    type=str,
    help="Исполнитель",
    autocompletion=get_assignees,
    template_var="assignee.name",
)
def create_issue(
    jira: JiraWrapper,
    template: Optional[dict],
    project: str,
    issue_type: str,
    summary: str,
    assignee: str,
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

    created_issue = jira.create_issue(fields=fields, template=template)

    click.echo(f"Created issue: {jira.server}/browse/{created_issue.key}")


@click.command()
@add_config_option
@add_jira_options("jira")
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


@click.command()
@add_config_option
@add_jira_options("jira")
@skip_config_option
@click.argument("issue_id", type=str, required=True)
def get_issue(
    jira: JiraWrapper,
    issue_id: str,
) -> None:
    """Получить все доступные поля Issue по ISSUE_ID."""
    issue = jira.get_issue(issue_id=issue_id)

    fields = issue.lib_issue.raw["fields"]

    yaml_string = yaml.dump(fields, allow_unicode=True)

    click.echo(yaml_string)
