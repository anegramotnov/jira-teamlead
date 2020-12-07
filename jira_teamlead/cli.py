import io
from typing import Callable, Tuple
from urllib.parse import urlparse

import click
import yaml

from jira_teamlead import jtl_fields
from jira_teamlead.jira_wrapper import JiraWrapper, SuperIssue


def validate_jira_auth(
    ctx: click.Context, param: click.Parameter, value: str
) -> Tuple[str, str]:
    """Валидация параметра --user."""
    try:
        value.encode("ascii")
    except UnicodeEncodeError:
        raise click.BadParameter("ожидаются символы ASCII")

    splitted_parts = value.split(":")
    if len(splitted_parts) != 2 or not all(splitted_parts):
        raise click.BadParameter("ожидается формат 'login:password'")

    login, password = splitted_parts

    return login, password


def validate_jira_server(ctx: click.Context, param: click.Parameter, value: str) -> str:
    """Валидация и преобразование параметра --jira-host."""
    url = urlparse(value)

    if not all([url.scheme, url.netloc]):
        raise click.BadParameter("ожидается формат 'http[s]://jira.host.net'")

    return f"{url.scheme}://{url.netloc}"


common_options = (
    click.option(
        "-js",
        "--server",
        required=True,
        callback=validate_jira_server,
        envvar="JTL_SERVER",
        help="Cервер Jira",
    ),
    click.option(
        "-ja",
        "--auth",
        required=True,
        callback=validate_jira_auth,
        envvar="JTL_AUTH",
        help="Учетные данные в формате 'login:password'",
    ),
)


def add_common_jtl_options(command: Callable) -> Callable:
    for option in reversed(common_options):
        command = option(command)
    return command


@click.group()
def jtl() -> None:
    """Инструмент автоматизации создания Issue в Jira."""
    import dotenv

    dotenv.load_dotenv(verbose=True)


@jtl.command()
@add_common_jtl_options
@click.option("-p", "--project", required=True, type=str, help="Ключ проекта")
@click.option("-t", "--type", "issue_type", required=True, type=str, help="Тип Issue")
@click.option("-s", "--summary", required=True, type=str, help="Название задачи")
def create_issue(
    server: str, auth: Tuple[str, str], project: str, issue_type: str, summary: str
) -> None:
    """Создание Issue."""
    jira = JiraWrapper(server=server, auth=auth)

    fields = {
        "project": {
            "key": project,
        },
        "issuetype": {
            "name": issue_type,
        },
        "summary": summary,
    }
    created_issue = jira.create_issue(fields=fields)

    click.echo(f"Created issue: {server}/browse/{created_issue.key}")


@jtl.command()
@add_common_jtl_options
@click.argument("issue_set_file", type=click.File("r", encoding="utf-8"))
def create_issue_set(
    server: str, auth: Tuple[str, str], issue_set_file: io.TextIOWrapper
) -> None:
    """Создание набора Issue из yaml-файла ISSUE_SET_FILE."""
    jira = JiraWrapper(server=server, auth=auth)
    issue_set_data = yaml.safe_load(issue_set_file)

    issue_set = issue_set_data[jtl_fields.ISSUE_SET_FIELD]
    issue_template = issue_set_data.get(jtl_fields.TEMPLATE_FIELD)

    issues = jira.create_issue_set(
        issue_set=issue_set,
        issue_template=issue_template,
    )

    for issue in issues:
        if isinstance(issue, SuperIssue):
            click.echo(f"Created super-issue: {server}/browse/{issue.key}")
            for sub_issue in issue.sub_issues:
                click.echo(f"    Created sub-issue: {server}/browse/{sub_issue.key}")
        else:
            click.echo(f"Created issue: {server}/browse/{issue.key}")


@jtl.command()
@add_common_jtl_options
@click.option("-p", "--project", required=True, type=str, help="Ключ проекта")
@click.argument("search_string", type=str, required=False)
def search_users(
    server: str,
    auth: Tuple[str, str],
    project: str,
    search_string: str,
) -> None:
    """Показать логины, доступные для поля assignee.

    Доступна фильтрация по SEARCH_STRING.
    """
    jira = JiraWrapper(server=server, auth=auth)

    users = jira.search_users(project=project, search_string=search_string)

    for user in users:
        click.echo(f"{user.name} ({user.displayName}, {user.emailAddress})")


@jtl.command()
@add_common_jtl_options
@click.argument("issue_id", type=str, required=True)
def get_issue(
    server: str,
    auth: Tuple[str, str],
    issue_id: str,
) -> None:
    """Получить все доступные поля Issue по ISSUE_ID."""
    jira = JiraWrapper(server=server, auth=auth)

    issue = jira.get_issue(issue_id=issue_id)

    fields = issue.lib_issue.raw["fields"]

    yaml_string = yaml.dump(fields, allow_unicode=True)

    click.echo(yaml_string)
