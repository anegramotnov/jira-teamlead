import io
from typing import Any, Callable, Optional, Tuple
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


def set_template_to_ctx(
    ctx: click.Context, param: click.Parameter, value: Optional[io.TextIOWrapper]
) -> Optional[dict]:
    if value is not None:
        template = yaml.safe_load(value)
        ctx.params["template"] = template
        return template
    else:
        return None


class IssueTemplateOption(click.Option):
    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        template_var = kwargs.pop("template_var")
        super().__init__(*args, **kwargs)
        self.template_var = template_var

    def value_from_template(self, ctx: click.Context) -> Optional[str]:
        if self.template_var is not None:
            parts = self.template_var.split(".")
            value = ctx.params["template"]
            for part in parts:
                value = value.get(part)
                if value is None:
                    return None
            return value
        else:
            return None

    def consume_value(self, ctx: click.Context, opts: dict) -> Any:
        value = opts.get(self.name)
        if value is None:
            value = self.value_from_envvar(ctx)
        if value is None:
            value = self.value_from_template(ctx)
        if value is None:
            value = ctx.lookup_default(self.name)
        return value


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
@click.option(
    "-tmpl",
    "--template",
    required=False,
    callback=set_template_to_ctx,
    type=click.File(),
    envvar="JTL_ISSUE_TEMPLATE",
)
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
def create_issue(
    server: str,
    auth: Tuple[str, str],
    template: Optional[dict],
    project: str,
    issue_type: str,
    summary: str,
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

    created_issue = jira.create_issue(fields=fields, template=template)

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
        template=issue_template,
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
