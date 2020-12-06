import io
from pprint import pformat
from urllib.parse import urlparse

import click
import yaml

from jira_teamlead.jira import JiraServer


def validate_user(ctx: click.Context, param: click.Parameter, value: str) -> str:
    """Валидация параметра --user."""
    splitted_parts = value.split(":")
    if len(splitted_parts) != 2 or not all(splitted_parts):
        raise click.BadParameter("ожидается формат 'login:password'")

    try:
        value.encode("ascii")
    except UnicodeEncodeError:
        raise click.BadParameter("ожидаются символы ASCII")

    return value


def validate_jira_host(ctx: click.Context, param: click.Parameter, value: str) -> str:
    """Валидация и преобразование параметра --jira-host."""
    url = urlparse(value)

    if not all([url.scheme, url.netloc]):
        raise click.BadParameter("ожидается формат 'http[s]://jira.host.net'")

    return f"{url.scheme}://{url.netloc}"


@click.group()
def cli() -> None:
    """Инструмент автоматизации работы в Jira."""


@cli.command()
@click.option("-jh", "--jira-host", required=True, callback=validate_jira_host)
@click.option("-u", "--user", required=True, callback=validate_user)
@click.option("-p", "--project", required=True, type=str)
@click.option("-t", "--type", "issue_type", required=True, type=str)
@click.option("-s", "--summary", required=True, type=str)
def create_issue(
    jira_host: str, user: str, project: str, issue_type: str, summary: str
) -> None:
    jira = JiraServer(host=jira_host, auth_string=user)

    create_payload = {
        "fields": {
            "project": {
                "key": project,
            },
            "issuetype": {
                "name": issue_type,
            },
            "summary": summary,
        }
    }
    response = jira.post("/rest/api/2/issue", create_payload)
    click.echo(pformat(response))


@cli.command()
@click.option("-jh", "--jira-host", required=True, callback=validate_jira_host)
@click.option("-u", "--user", required=True, callback=validate_user)
@click.option("--dry-run", is_flag=True)
@click.argument("issues_source_file", type=click.File("r", encoding="utf-8"))
def create_issues(
    jira_host: str, user: str, dry_run: bool, issues_source_file: io.TextIOWrapper
) -> None:
    jira = JiraServer(host=jira_host, auth_string=user, dry_run=dry_run)

    issues_source_data = yaml.safe_load(issues_source_file)

    issues_data = issues_source_data["issues"]
    project = issues_source_data["project"]

    for issue_data in issues_data:
        issue_data["project"] = project
        issue_payload = {"fields": issue_data}

        response: dict = jira.post("/rest/api/2/issue", payload=issue_payload)

        if not dry_run:
            click.echo(f"Created issue: {jira.host}/browse/{response['key']}")


@cli.command()
@click.option("-jh", "--jira-host", required=True, callback=validate_jira_host)
@click.option("-u", "--user", required=True, callback=validate_user)
@click.option("-p", "--project", required=True, type=str)
@click.argument("username", type=str, required=False)
def find_user(
    jira_host: str,
    user: str,
    project: str,
    username: str,
) -> None:
    jira = JiraServer(host=jira_host, auth_string=user)

    response = jira.get(
        "/rest/api/2/user/assignable/search",
        params={"project": project, "username": username},
    )

    for user in response:
        if user["deleted"] or not user["active"]:
            continue
        aliases = [user["displayName"], user["emailAddress"]]
        click.echo("{0} ({1})".format(user["name"], ", ".join(aliases)))
