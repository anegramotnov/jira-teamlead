from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from jira import JIRA, Issue, User


@dataclass
class IssueWrapper:
    lib_issue: Issue
    key: str
    summary: str


@dataclass
class SubIssue(IssueWrapper):
    pass


@dataclass
class SuperIssue(IssueWrapper):
    sub_issues: List[SubIssue] = field(default_factory=list)


@dataclass
class UserWrapper:
    lib_user: User
    name: str
    displayName: str
    emailAddress: str


class JiraWrapper:
    jira: JIRA

    SUB_ISSUE_FIELD = "sub_issues"

    DESCRIPTION_FIELD = "description"
    SUB_ISSUE_DESCRIPTION_TEMPLATE = """
    Основная задача: {super_issue_key}
    ----
    {description}"""

    def __init__(self, server: str, auth: Tuple[str, str]) -> None:
        self.jira = JIRA(server=server, auth=auth)

    def create_issue(self, fields: dict) -> IssueWrapper:
        """Создать Issue."""
        created_lib_issue = self.jira.create_issue(**fields)
        issue = IssueWrapper(
            lib_issue=created_lib_issue,
            key=created_lib_issue.key,
            summary=created_lib_issue.fields.summary,
        )
        return issue

    def create_issue_set(
        self, project: dict, issue_set: List[dict]
    ) -> List[IssueWrapper]:
        issues: List[IssueWrapper] = []

        for issue_data in issue_set:
            issue_data["project"] = project

            if self.SUB_ISSUE_FIELD in issue_data:
                sub_issues = issue_data.pop(self.SUB_ISSUE_FIELD)
                super_issue = self.create_super_issue(
                    fields=issue_data, sub_issues=sub_issues
                )
                issues.append(super_issue)
            else:
                issue = self.create_issue(fields=issue_data)
                issues.append(issue)

        return issues

    def create_super_issue(self, fields: dict, sub_issues: List[dict]) -> SuperIssue:
        """Создать задачу, содержащее подзадачи."""
        created_issue = self.create_issue(fields=fields)

        issue = SuperIssue(
            lib_issue=created_issue.lib_issue,
            key=created_issue.key,
            summary=created_issue.summary,
        )

        for sub_issue_extra_fields in sub_issues:
            sub_issue = self.create_sub_issue(
                fields=sub_issue_extra_fields,
                super_issue_key=issue.key,
                super_issue_fields=fields,
            )
            issue.sub_issues.append(sub_issue)

        return issue

    def _update_sub_issue_description(
        self, sub_issue_fields: dict, super_issue_key: str
    ) -> None:
        old_description = sub_issue_fields.get(self.DESCRIPTION_FIELD)
        new_description = self.SUB_ISSUE_DESCRIPTION_TEMPLATE.format(
            super_issue_key=super_issue_key, description=old_description
        )
        sub_issue_fields[self.DESCRIPTION_FIELD] = new_description

    def _inherit_super_issue_fields(
        self, sub_issue_fields: dict, super_issue_fields: dict
    ) -> dict:
        fields = {}
        fields.update(super_issue_fields)
        fields.update(sub_issue_fields)
        return fields

    def create_sub_issue(
        self, fields: dict, super_issue_key: str, super_issue_fields: dict
    ) -> SubIssue:
        """Создать подзадачу, относящуюся к задаче."""
        sub_issue_fields = self._inherit_super_issue_fields(
            sub_issue_fields=fields, super_issue_fields=super_issue_fields
        )

        self._update_sub_issue_description(
            sub_issue_fields=sub_issue_fields, super_issue_key=super_issue_key
        )

        created_issue = self.create_issue(fields=sub_issue_fields)

        sub_issue = SubIssue(
            lib_issue=created_issue.lib_issue,
            key=created_issue.key,
            summary=created_issue.summary,
        )
        return sub_issue

    def search_users(
        self, project: str, username: Optional[str] = None
    ) -> List[UserWrapper]:
        """Вывести логины пользователей, доступные для поля assignee."""
        lib_users = self.jira.search_assignable_users_for_issues(
            username=username, project=project
        )
        users = []
        for lib_user in lib_users:
            if not lib_user.deleted and lib_user.active:
                users.append(
                    UserWrapper(
                        lib_user=lib_user,
                        name=lib_user.name,
                        displayName=lib_user.displayName,
                        emailAddress=lib_user.emailAddress,
                    )
                )

        return users
