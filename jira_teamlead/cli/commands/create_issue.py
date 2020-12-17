import webbrowser
from typing import Optional

import click

from jira_teamlead.cli.autocompletion import (
    assignee_autocompletion,
    autocompletion_with_jira,
    issue_type_autocompletion,
    project_autocompletion,
)
from jira_teamlead.cli.options.config import (
    add_config_option,
    from_config_fallback,
    skip_config_option,
)
from jira_teamlead.cli.options.fallback import FallbackOption
from jira_teamlead.cli.options.issue import PROJECT_CLICK_PARAM
from jira_teamlead.cli.options.jira import add_jira_options
from jira_teamlead.cli.options.template import (
    TEMPLATE_CLICK_PARAM,
    from_template_fallback,
    parse_yaml_option,
)
from jira_teamlead.jira_wrapper import JiraWrapper


@click.command()
@add_config_option
@add_jira_options("jira")
@click.option(
    "-tl",
    "--template",
    TEMPLATE_CLICK_PARAM,
    cls=FallbackOption,
    type=click.File("r", encoding="utf-8"),
    required=False,
    callback=parse_yaml_option,
    help="Файл с шаблоном Issue",
    fallback=from_config_fallback(section="defaults.create-issue", option="template"),
)
@click.option(
    "-p",
    "--project",
    PROJECT_CLICK_PARAM,
    cls=FallbackOption,
    type=str,
    required=True,
    autocompletion=autocompletion_with_jira(project_autocompletion),
    prompt=True,
    help="Ключ проекта",
    fallback=[
        from_template_fallback(query="project.key"),
        from_config_fallback(section="defaults", option="project"),
    ],
)
@skip_config_option
@click.option(
    "-t",
    "--type",
    "issue_type",
    cls=FallbackOption,
    type=str,
    required=True,
    autocompletion=autocompletion_with_jira(issue_type_autocompletion),
    prompt=True,
    help="Тип Issue",
    fallback=from_template_fallback("issuetype.name"),
)
@click.option(
    "-a",
    "--assignee",
    type=str,
    required=False,
    autocompletion=autocompletion_with_jira(assignee_autocompletion),
    help="Исполнитель",
)
@click.option(
    "-s",
    "--summary",
    type=str,
    required=True,
    prompt=True,
    help="Название задачи",
)
@click.option(
    "--open/--no-open",
    "open_link",
    cls=FallbackOption,
    required=True,
    default=True,
    is_flag=True,
    help="Открыть созданные задачи в браузере",
    fallback=from_config_fallback(section="defaults.create-issue", option="open_link"),
)
def create_issue(
    jira: JiraWrapper,
    template: Optional[dict],
    project: str,
    issue_type: str,
    assignee: Optional[str],
    summary: str,
    open_link: bool,
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

    click.echo(f"Created issue: {created_issue.link}")
    if open_link:
        webbrowser.open_new_tab(created_issue.link)
