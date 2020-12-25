import click

from jira_teamlead.cli.commands.config import config_group
from jira_teamlead.cli.commands.create_issue import create_issue
from jira_teamlead.cli.commands.create_issue_set import create_issue_set
from jira_teamlead.cli.commands.get_issue import get_issue
from jira_teamlead.cli.commands.search_users import search_users

context_settings = dict(max_content_width=120)  # noqa: C408


@click.group(context_settings=context_settings)
def jtl() -> None:
    """Инструмент автоматизации создания Issue в Jira."""


def init_jtl() -> None:
    jtl.add_command(search_users)
    jtl.add_command(get_issue)
    jtl.add_command(create_issue)
    jtl.add_command(create_issue_set)
    jtl.add_command(config_group)


init_jtl()
