from jira_teamlead.config import (
    DEFAULTS_CREATE_ISSUE_SECTION,
    DEFAULTS_SECTION,
    JIRA_SECTION,
)

CONFIG_SHORT = "-jc"
CONFIG_FULL = "--config"
CONFIG_PARAM = "config"
CONFIG_HELP = "Путь к файлу конфигурации"

JIRA_PARAM = "jira"

SERVER_SHORT = "-js"
SERVER_FULL = "--server"
SERVER_PARAM = "server"
SERVER_HELP = "Cервер Jira"
SERVER_CONFIG = (JIRA_SECTION, SERVER_PARAM)

LOGIN_SHORT = "-jl"
LOGIN_FULL = "--login"
LOGIN_PARAM = "login"
LOGIN_HELP = "Логин в Jira"
LOGIN_CONFIG = (JIRA_SECTION, LOGIN_PARAM)

PASSWORD_SHORT = "-jp"
PASSWORD_FULL = "--password"
PASSWORD_PARAM = "password"
PASSWORD_HELP = "Пароль в Jira"
PASSWORD_CONFIG = (JIRA_SECTION, PASSWORD_PARAM)

TEMPLATE_SHORT = "-tl"
TEMPLATE_FULL = "--template"
TEMPLATE_PARAM = "issue_template"
TEMPLATE_HELP = "Файл с шаблоном Issue"
TEMPLATE_CONFIG = (DEFAULTS_CREATE_ISSUE_SECTION, TEMPLATE_PARAM)

PROJECT_SHORT = "-p"
PROJECT_FULL = "--project"
PROJECT_PARAM = "project"
PROJECT_HELP = "Ключ проекта"
PROJECT_CONFIG = (DEFAULTS_SECTION, PROJECT_PARAM)
PROJECT_CONFIG_HELP = PROJECT_HELP + " по умолчанию"
PROJECT_TEMPLATE_QUERY = "project.key"

OPEN_LINK_FULL = "--open/--no-open"
OPEN_LINK_PARAM = "open_in_browser"
OPEN_LINK_HELP = "Открыть созданные задачи в браузере"
OPEN_LINK_CONFIG = (DEFAULTS_CREATE_ISSUE_SECTION, OPEN_LINK_PARAM)
OPEN_LINK_CONFIG_HELP = "Открывать созданные задачи в браузере"

LOCAL_CONFIG_FULL = "--local/--global"
LOCAL_CONFIG_PARAM = "global"
LOCAL_CONFIG_HELP = "Локальная конфигурация (в текущей директории)"

ISSUE_TYPE_SHORT = "-t"
ISSUE_TYPE_FULL = "--type"
ISSUE_TYPE_PARAM = "issue_type"
ISSUE_TYPE_HELP = "Тип Issue"
ISSUE_TYPE_TEMPLATE_QUERY = "issuetype.name"

ASSIGNEE_SHORT = "-a"
ASSIGNEE_FULL = "--assignee"
ASSIGNEE_PARAM = "assignee"
ASSIGNEE_HELP = "Исполнитель"

SUMMARY_SHORT = "-s"
SUMMARY_FULL = "--summary"
SUMMARY_PARAM = "summary"
SUMMARY_HELP = "Название задачи"

CONFIG_VALUES_PARAM = "config_values"
