from typing import Callable, List, Optional

import click

from jira_teamlead.cli.options.constants import PROJECT_PARAM
from jira_teamlead.cli.options.jira import set_jira_to_params
from jira_teamlead.jira_wrapper import IssueType, JiraWrapper, Project


def autocompletion_with_jira(autocompletion: Callable) -> Callable:
    def autocompletion_wrapper(
        ctx: click.Context, args: list, incomplete: str
    ) -> List[str]:
        jira = set_jira_to_params(ctx.params)
        return autocompletion(jira, ctx.params, incomplete)

    return autocompletion_wrapper


def is_empty_or_match(search: Optional[str], name: str) -> bool:
    if not search:
        return True
    normalized_search = search.strip().lower()
    normalized_name = name.lower()
    return normalized_name.startswith(normalized_search)


def search_issue_types(
    jira: JiraWrapper,
    search_string: Optional[str],
) -> List[IssueType]:
    issue_types = jira.get_issue_types()

    found: List[IssueType] = []
    for issue_type in issue_types:
        if is_empty_or_match(search_string, issue_type.name):
            found.append(issue_type)
    return found


def search_projects(jira: JiraWrapper, search_string: Optional[str]) -> List[Project]:
    projects = jira.get_projects()

    found: List[Project] = []
    for project in projects:
        if is_empty_or_match(search_string, project.key) or is_empty_or_match(
            search_string, project.name
        ):
            found.append(project)

    return found


def assignee_autocompletion(
    jira: JiraWrapper, params: dict, incomplete: str
) -> List[str]:
    project: str = params[PROJECT_PARAM]
    users = jira.search_users(project=project, search_string=incomplete)
    usernames = [u.name for u in users]
    return usernames


def issue_type_autocompletion(
    jira: JiraWrapper, params: dict, incomplete: str
) -> List[str]:

    issue_types = search_issue_types(jira=jira, search_string=incomplete)

    return [issue_type.name for issue_type in issue_types]


def project_autocompletion(
    jira: JiraWrapper, params: dict, incomplete: str
) -> List[str]:

    projects = search_projects(jira=jira, search_string=incomplete)

    return [project.key for project in projects]
