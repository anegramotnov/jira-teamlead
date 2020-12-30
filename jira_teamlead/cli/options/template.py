from pathlib import Path
from typing import Any, List, Optional

import click
import yaml
from yaml.parser import ParserError as YamlParserError

from jira_teamlead.issue_template import IssueTemplate
from jira_teamlead.type_aliases import IssueFieldsT


class YamlType(click.ParamType):
    name = "yaml_file"
    inner_file_type: click.File

    def __init__(self) -> None:
        self.inner_file_type = click.File("r", encoding="utf-8")
        self._file = None

    def convert(
        self, value: str, param: Optional[click.Parameter], ctx: Optional[click.Context]
    ) -> Any:

        file = self.inner_file_type.convert(value=value, param=param, ctx=ctx)

        try:
            yaml_content = yaml.safe_load(file)
        except YamlParserError as e:
            raise click.BadParameter(
                "Ошибка при парсинге YAML в {0}:{1}:{2}: {3}".format(
                    e.problem_mark.name,
                    e.problem_mark.line + 1,
                    e.problem_mark.column + 1,
                    e.problem,
                )
            )

        return yaml_content


class IssueTemplateType(YamlType):
    def convert(
        self, value: str, param: Optional[click.Parameter], ctx: Optional[click.Context]
    ) -> IssueTemplate:
        yaml_content = super().convert(value=value, param=param, ctx=ctx)
        if yaml_content is None:
            fields = {}
        else:
            fields = yaml_content
        if not isinstance(fields, dict):
            raise click.BadParameter(
                "Неверный формат файла шаблона задачи {0}".format(value)
            )

        return IssueTemplate(path=Path(value), fields=fields)


class IssueSetType(YamlType):
    def convert(
        self, value: str, param: Optional[click.Parameter], ctx: Optional[click.Context]
    ) -> List[IssueFieldsT]:
        yaml_content = super().convert(value=value, param=param, ctx=ctx)
        if yaml_content is None:
            issue_set = []
        else:
            issue_set = yaml_content
        if not isinstance(issue_set, list):
            raise click.BadParameter(
                "Неверный формат файла набора задач {0}".format(value)
            )
        for fields in issue_set:
            if not isinstance(fields, dict):
                raise click.BadParameter(
                    "Неверный формат файла набора задач {0}".format(value)
                )

        return issue_set
