import dataclasses
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar

import jira.resources
from jira.client import JIRA

from jira_teamlead import jtl_fields

T_Issue = TypeVar("T_Issue", bound="Issue")


@dataclasses.dataclass
class Issue:
    raw: Dict[str, Any]
    key: str
    summary: str
    link: str

    @classmethod
    def from_resource(
        cls: Type[T_Issue], issue_resource: jira.resources.Issue, server: str
    ) -> T_Issue:
        link = "{0}/browse/{1}".format(server, issue_resource.key)
        return cls(
            raw=issue_resource.raw,
            key=issue_resource.key,
            summary=issue_resource.fields.summary,
            link=link,
        )

    @classmethod
    def from_issue(cls: Type[T_Issue], issue: "Issue") -> T_Issue:
        issue_params = {}
        for issue_field in dataclasses.fields(Issue):
            issue_params[issue_field.name] = getattr(issue, issue_field.name)
        return cls(**issue_params)


@dataclasses.dataclass
class SubIssue(Issue):
    pass


@dataclasses.dataclass
class SuperIssue(Issue):
    sub_issues: List[SubIssue] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class User:
    raw: Dict[str, Any]
    name: str
    displayName: str
    emailAddress: str

    @classmethod
    def from_resource(cls, user_resource: jira.resources.User) -> "User":
        return cls(
            raw=user_resource.raw,
            name=user_resource.name,
            displayName=user_resource.displayName,
            emailAddress=user_resource.emailAddress,
        )


@dataclasses.dataclass
class IssueType:
    raw: Dict[str, Any]
    id: str
    name: str

    @classmethod
    def from_resource(
        cls, issue_type_resource: jira.resources.IssueType
    ) -> "IssueType":
        return cls(
            raw=issue_type_resource.raw,
            id=issue_type_resource.id,
            name=issue_type_resource.name,
        )


@dataclasses.dataclass
class Project:
    raw: Dict[str, Any]
    id: str
    key: str
    name: str

    @classmethod
    def from_resource(
        cls,
        project_resource: jira.resources.Project,
    ) -> "Project":
        return cls(
            raw=project_resource.raw,
            id=project_resource.id,
            key=project_resource.key,
            name=project_resource.name,
        )


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

    def create_issue(self, fields: dict, template: Optional[dict] = None) -> Issue:
        """Создать Issue."""
        issue_fields = self._override_from_template(
            original_fields=fields, template_fields=template
        )

        issue_resource = self.jira.create_issue(**issue_fields)

        issue = Issue.from_resource(issue_resource=issue_resource, server=self.server)

        return issue

    def create_issue_set(
        self,
        issues: List[dict],
        template: Optional[dict] = None,
    ) -> List[Issue]:
        templated_issues: List[Issue] = []

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

        issue = SuperIssue.from_issue(issue=created_issue)

        super_issue = SuperIssue.from_issue(issue=created_issue)

        for sub_issue_extra_fields in sub_issues:
            sub_issue = self.create_sub_issue(
                fields=sub_issue_extra_fields,
                super_issue_key=issue.key,
                super_issue_fields=fields,
            )
            super_issue.sub_issues.append(sub_issue)

        return super_issue

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
        new_fields = {}
        new_fields.update(super_issue_fields)
        new_fields.update(sub_issue_fields)
        return new_fields

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

        sub_issue = SubIssue.from_issue(issue=created_issue)

        return sub_issue

    def search_users(
        self, project: str, search_string: Optional[str] = None
    ) -> List[User]:
        """Вывести логины пользователей, доступные для поля assignee."""
        user_resources = self.jira.search_assignable_users_for_issues(
            username=search_string, project=project
        )
        users = []
        for user_resource in user_resources:
            if not user_resource.deleted and user_resource.active:
                users.append(User.from_resource(user_resource))

        return users

    def get_issue(self, issue_id: str) -> Issue:
        issue_resource = self.jira.issue(id=issue_id)

        issue = Issue.from_resource(issue_resource=issue_resource, server=self.server)

        return issue

    def get_issue_types(self) -> List[IssueType]:
        issue_type_resources = self.jira.issue_types()

        issue_types = [
            IssueType.from_resource(resource) for resource in issue_type_resources
        ]

        return issue_types

    def get_projects(self) -> List[Project]:
        project_resources = self.jira.projects()

        projects = [Project.from_resource(resource) for resource in project_resources]

        return projects
