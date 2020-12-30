from copy import deepcopy
from pathlib import Path
from typing import Any, Optional

from jira_teamlead.type_aliases import IssueFieldsT


def inherit_fields(fields: IssueFieldsT, base: IssueFieldsT) -> IssueFieldsT:
    result: IssueFieldsT = dict()
    result.update(base)
    result.update(fields)
    return result


class IssueTemplate:
    path: Path
    _fields: IssueFieldsT

    def __init__(self, path: Path, fields: IssueFieldsT) -> None:
        self.path = path
        self._fields = fields

    @property
    def fields(self) -> IssueFieldsT:
        return deepcopy(self._fields)

    def apply_template(self, issue_fields: IssueFieldsT) -> IssueFieldsT:
        return inherit_fields(fields=issue_fields, base=self.fields)

    def get(self, query: str) -> Optional[str]:
        parts = query.split(".")
        value: Any = self.fields
        for part in parts:
            value = value.get(part)
            if value is None:
                return None
        return value
