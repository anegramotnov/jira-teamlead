import base64
from pprint import pformat
from urllib.parse import urljoin, urlparse

import click
import requests


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


class JiraServer:
    host: str
    auth_string: str
    session: requests.Session

    def __init__(self, host: str, auth_string: str) -> None:
        self.host = host
        self.auth_string = auth_string
        self.session = requests.Session()
        self.session.headers.update(self._get_auth_header())

    def _get_auth_header(self) -> dict:
        encoded_auth = base64.b64encode(self.auth_string.encode()).decode()

        auth_header = {"Authorization": f"Basic {encoded_auth}"}
        return auth_header

    def _get_url(self, path: str) -> str:
        return urljoin(self.host, path)

    def get(self, path: str) -> dict:
        url = self._get_url(path)
        response = self.session.get(url)
        return response.json()

    def post(self, path: str, payload: dict) -> dict:
        url = self._get_url(path)
        response = self.session.post(url, json=payload)
        return response.json()


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


if __name__ == "__main__":
    cli()
