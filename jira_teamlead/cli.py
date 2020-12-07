import io
from typing import Tuple
from urllib.parse import urlparse

import click
import yaml

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


@click.group()
def cli() -> None:
    """Инструмент автоматизации работы в Jira."""
    import dotenv

    dotenv.load_dotenv(verbose=True)


@cli.command()
@click.option(
    "-js",
    "--server",
    required=True,
    callback=validate_jira_server,
    envvar="JTL_SERVER",
)
@click.option(
    "-a", "--auth", required=True, callback=validate_jira_auth, envvar="JTL_AUTH"
)
@click.option("-p", "--project", required=True, type=str)
@click.option("-t", "--type", "issue_type", required=True, type=str)
@click.option("-s", "--summary", required=True, type=str)
def create_issue(
    server: str, auth: Tuple[str, str], project: str, issue_type: str, summary: str
) -> None:
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


@cli.command()
@click.option(
    "-js",
    "--server",
    required=True,
    callback=validate_jira_server,
    envvar="JTL_SERVER",
)
@click.option(
    "-a", "--auth", required=True, callback=validate_jira_auth, envvar="JTL_AUTH"
)
@click.argument("issue_set_file", type=click.File("r", encoding="utf-8"))
def create_issue_set(
    server: str, auth: Tuple[str, str], issue_set_file: io.TextIOWrapper
) -> None:

    jira = JiraWrapper(server=server, auth=auth)
    issue_set_data = yaml.safe_load(issue_set_file)

    issue_set = issue_set_data["issues"]
    issue_template = issue_set_data.get("template")

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


# TODO: Вынести общие параметры с envvar в отдельный декоратор,
#       который прокинет готовый экземпляр jira
@cli.command()
@click.option(
    "-js",
    "--server",
    required=True,
    callback=validate_jira_server,
    envvar="JTL_SERVER",
)
@click.option(
    "-a", "--auth", required=True, callback=validate_jira_auth, envvar="JTL_AUTH"
)
@click.option("-p", "--project", required=True, type=str)
@click.argument("username", type=str, required=False)
def search_users(
    server: str,
    auth: Tuple[str, str],
    project: str,
    username: str,
) -> None:
    """Вывести логины пользователей, доступные для поля assignee."""
    jira = JiraWrapper(server=server, auth=auth)

    users = jira.search_users(project=project, username=username)

    for user in users:
        click.echo(f"{user.name} ({user.displayName}, {user.emailAddress})")
