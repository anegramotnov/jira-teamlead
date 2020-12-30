from http.client import responses
from typing import Any, List, NamedTuple, Optional

import click
from click._compat import get_text_stderr

from jira_teamlead.cli.options.fallback import FallbackOption
from jira_teamlead.jira_wrapper import JiraError


class JiraFieldError(NamedTuple):
    message: str
    param: Optional[click.Parameter]
    param_hint: Optional[str]


class JiraResponseError(click.UsageError):
    exit_code = 3

    error_message_offset = 4

    status_code: int
    _field_errors: List[JiraFieldError]
    _errors: List[str]

    def __init__(self, message: str, status_code: int, ctx: click.Context) -> None:
        self.status_code = status_code
        self._field_errors = []
        self._errors = []
        super().__init__(message, ctx=ctx)

    def add_field_error(
        self,
        message: str,
        param: Optional[click.Parameter] = None,
        param_hint: Optional[str] = None,
    ) -> None:
        self._field_errors.append(
            JiraFieldError(message=message, param=param, param_hint=param_hint)
        )

    def add_error(self, message: str) -> None:
        self._errors.append(message)

    def format_message(self) -> str:
        error_messages = [self.format_error_message(error) for error in self._errors]
        field_error_messages = [
            self.format_field_error_message(**error._asdict())
            for error in self._field_errors
        ]
        message = "\n".join(error_messages + field_error_messages)
        return message

    def format_error_message(self, message: str) -> str:
        return " " * self.error_message_offset + message

    def format_field_error_message(
        self, message: str, param: Optional[click.Parameter], param_hint: str
    ) -> str:
        if param_hint is not None:
            param_hint = param_hint
        elif param is not None:
            param_hint = param.get_error_hint(self.ctx)
        else:
            return " " * self.error_message_offset + "Invalid value: {0}".format(
                self.message
            )
        return (
            " " * self.error_message_offset
            + 'Invalid value for field {0}: "{1}"'.format(param_hint, message)
        )

    def show(self, file: Any = None) -> None:
        if file is None:
            file = get_text_stderr()

        click.echo(
            "Jira REST API Error ({0} {1}):\n{2} ".format(
                self.status_code, responses[self.status_code], self.format_message()
            ),
            file=file,
        )


def get_fallback_param_from_ctx(
    ctx: click.Context, field_name: str
) -> Optional[click.Parameter]:
    field_param_map = {
        "issuetype": "issue_type",
    }

    param_name = field_param_map.get(field_name, field_name)

    found_params = [
        param
        for param in ctx.command.params
        if param.name == param_name and isinstance(param, FallbackOption)
    ]
    if found_params:
        return found_params[0]
    else:
        return None


# TODO: убрать специфическую обработку полей создания задачи из общей функции
def raise_jira_response_error(
    jira_error_wrapper: JiraError, ctx: click.Context
) -> None:
    if isinstance(jira_error_wrapper.response, dict):
        jira_response_error = JiraResponseError(
            message=jira_error_wrapper.message,
            status_code=jira_error_wrapper.status_code,
            ctx=ctx,  # noqa: B306
        )
        field_errors = jira_error_wrapper.response.get("errors", {})
        for field, message in field_errors.items():
            fallback_param = get_fallback_param_from_ctx(ctx=ctx, field_name=field)
            if fallback_param is not None:
                jira_response_error.add_field_error(
                    message=message, param=fallback_param
                )
            else:
                jira_response_error.add_field_error(
                    message=message,
                    param_hint="'{0}' (from template)".format(field),
                )
        error_messages = jira_error_wrapper.response.get("errorMessages", [])
        for error_message in error_messages:
            jira_response_error.add_error(message=error_message)
        raise jira_response_error
    else:
        raise
