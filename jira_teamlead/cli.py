import io
from typing import Tuple
from urllib.parse import urlparse

import click
import jira as jira_lib
import yaml


def validate_user(
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


def validate_jira_host(ctx: click.Context, param: click.Parameter, value: str) -> str:
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
    "-jh",
    "--jira-host",
    required=True,
    callback=validate_jira_host,
    envvar="JT_JIRA_HOST",
)
@click.option("-u", "--user", required=True, callback=validate_user, envvar="JT_USER")
@click.option("-p", "--project", required=True, type=str)
@click.option("-t", "--type", "issue_type", required=True, type=str)
@click.option("-s", "--summary", required=True, type=str)
def create_issue(
    jira_host: str, user: str, project: str, issue_type: str, summary: str
) -> None:
    jira = jira_lib.JIRA(jira_host, basic_auth=user)

    create_payload = {
        "project": {
            "key": project,
        },
        "issuetype": {
            "name": issue_type,
        },
        "summary": summary,
    }
    created_issue = jira.create_issue(**create_payload)

    click.echo(f"Created issue: {jira_host}/browse/{created_issue.key}")


@cli.command()
@click.option(
    "-jh",
    "--jira-host",
    required=True,
    callback=validate_jira_host,
    envvar="JT_JIRA_HOST",
)
@click.option("-u", "--user", required=True, callback=validate_user, envvar="JT_USER")
@click.argument("issues_source_file", type=click.File("r", encoding="utf-8"))
def create_issues(
    jira_host: str, user: str, issues_source_file: io.TextIOWrapper
) -> None:
    jira = jira_lib.JIRA(jira_host, basic_auth=user)

    issues_source_data = yaml.safe_load(issues_source_file)

    issues_data = issues_source_data["issues"]
    project = issues_source_data["project"]

    for issue_data in issues_data:
        issue_data["project"] = project

        created_issue = jira.create_issue(**issue_data)

        click.echo(f"Created issue: {jira_host}/browse/{created_issue.key}")


# TODO: Вынести общие параметры с envvar в отдельный декоратор
@cli.command()
@click.option(
    "-jh",
    "--jira-host",
    required=True,
    callback=validate_jira_host,
    envvar="JT_JIRA_HOST",
)
@click.option(
    "-u", "--user", "auth", required=True, callback=validate_user, envvar="JT_USER"
)
@click.option("-p", "--project", required=True, type=str)
@click.argument("username", type=str, required=False)
def find_user(
    jira_host: str,
    auth: str,
    project: str,
    username: str,
) -> None:
    jira = jira_lib.JIRA(jira_host, basic_auth=auth)

    users = jira.search_assignable_users_for_issues(username=username, project=project)

    for user in users:
        if user.deleted or not user.active:
            continue
        click.echo(f"{user.name} ({user.displayName}, {user.emailAddress})")
