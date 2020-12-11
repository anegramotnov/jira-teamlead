import click

from .issues_commands import create_issue, create_issue_set, get_issue
from .users_commands import search_users


@click.group()
def jtl() -> None:
    """Инструмент автоматизации создания Issue в Jira."""


def init_jtl() -> None:
    jtl.add_command(search_users)
    jtl.add_command(get_issue)
    jtl.add_command(create_issue)
    jtl.add_command(create_issue_set)


init_jtl()
