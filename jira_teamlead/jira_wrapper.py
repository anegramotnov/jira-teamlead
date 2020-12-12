from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Type, TypeVar

from jira import JIRA, Issue, User

from jira_teamlead import jtl_fields

IssueType = TypeVar("IssueType", bound="IssueWrapper")


@dataclass
class IssueWrapper:
    lib_issue: Issue
    key: str
    summary: str

    @classmethod
    def from_lib(cls: Type[IssueType], issue: Issue) -> IssueType:
        return cls(lib_issue=issue, key=issue.key, summary=issue.fields.summary)


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
    server: str

    DESCRIPTION_FIELD = "description"
    SUB_ISSUE_DESCRIPTION_TEMPLATE = """
    Основная задача: {super_issue_key}
    ----
    {description}"""

    def __init__(self, server: str, auth: Tuple[str, str]) -> None:
        self.server = server
        self.jira = JIRA(server=self.server, auth=auth)

    def create_issue(
        self, fields: dict, template: Optional[dict] = None
    ) -> IssueWrapper:
        """Создать Issue."""
        issue_fields = self._override_from_template(
            original_fields=fields, template_fields=template
        )

        created_lib_issue = self.jira.create_issue(**issue_fields)

        issue = IssueWrapper.from_lib(issue=created_lib_issue)

        return issue

    def create_issue_set(
        self,
        issues: List[dict],
        template: Optional[dict] = None,
    ) -> List[IssueWrapper]:
        templated_issues: List[IssueWrapper] = []

        for original_issue_fields in issues:

            issue_fields = self._override_from_template(
                original_fields=original_issue_fields,
                template_fields=template,
            )

            if jtl_fields.SUB_ISSUE_FIELD in issue_fields:
                sub_issues = issue_fields.pop(jtl_fields.SUB_ISSUE_FIELD)
                super_issue = self.create_super_issue(
                    fields=issue_fields, sub_issues=sub_issues
                )
                templated_issues.append(super_issue)
            else:
                issue = self.create_issue(fields=issue_fields)
                templated_issues.append(issue)

        return templated_issues

    def create_super_issue(self, fields: dict, sub_issues: List[dict]) -> SuperIssue:
        """Создать задачу, содержащее подзадачи."""
        created_issue = self.create_issue(fields=fields)

        issue = SuperIssue.from_lib(issue=created_issue.lib_issue)

        for sub_issue_extra_fields in sub_issues:
            sub_issue = self.create_sub_issue(
                fields=sub_issue_extra_fields,
                super_issue_key=issue.key,
                super_issue_fields=fields,
            )
            issue.sub_issues.append(sub_issue)

        return issue

    def _override_from_template(
        self, original_fields: dict, template_fields: Optional[dict] = None
    ) -> dict:
        if template_fields is None:
            return original_fields

        fields: dict = {}
        fields.update(template_fields)
        fields.update(original_fields)
        return fields

    def _update_sub_issue_description(
        self, sub_issue_fields: dict, super_issue_key: str
    ) -> None:
        old_description = sub_issue_fields.get(self.DESCRIPTION_FIELD)
        new_description = self.SUB_ISSUE_DESCRIPTION_TEMPLATE.format(
            super_issue_key=super_issue_key, description=old_description
        )
        sub_issue_fields[self.DESCRIPTION_FIELD] = new_description

    def _override_from_super_issue(
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
        sub_issue_fields = self._override_from_super_issue(
            sub_issue_fields=fields, super_issue_fields=super_issue_fields
        )

        self._update_sub_issue_description(
            sub_issue_fields=sub_issue_fields, super_issue_key=super_issue_key
        )

        created_issue = self.create_issue(fields=sub_issue_fields)

        sub_issue = SubIssue.from_lib(issue=created_issue.lib_issue)

        return sub_issue

    def search_users(
        self, project: str, search_string: Optional[str] = None
    ) -> List[UserWrapper]:
        """Вывести логины пользователей, доступные для поля assignee."""
        lib_users = self.jira.search_assignable_users_for_issues(
            username=search_string, project=project
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

    def get_issue(self, issue_id: str) -> IssueWrapper:
        lib_issue = self.jira.issue(id=issue_id)

        issue = IssueWrapper.from_lib(issue=lib_issue)

        return issue
