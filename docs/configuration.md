# Конфигурация

Конфигурация приложения может быть задана через конфигурационные файлы и
через параметры командной строки.

## Порядок поиска источников конфигурации

* Файл, указанный в параметре командной строки `-jc/--config`
* Файл `.jtl.cfg`, находящийся в директории, из которой запускается jtl
* Файл `~/.jtl.cfg`, находящийся в домашней директории пользователя

Это означает, что если не указан файл конфигурации в параметрах командной строки,
используется файл, находящийся в текущей директории.

Если в текущей директории нет файла конфигурации, то используется файл,
находящийся в домашней директории пользователя.

Если в домашней директории пользователя файл конфигурации отсутствует,
будут использованы параметры командной строки.

{% include "admonitions/prompt_note.md" %}

## Формат конфигурационного файла

    [jtl.jira]
    server = http://localhost:8080
    login = my_login
    password = my_password

    [jtl.defaults]
    project = DEV

    [jtl.defaults.create-issue]
    issue_template = default_issue.yaml
    open_in_browser = true  # or false


### Секция `jtl.jira`

Секция подключения к серверу Jira:

|Параметр в конфиг. файле | Параметр командной строки |Описание      |
|----------|------------------|--------------|
|`{{ c.SERVER_PARAM }}`|`{{ c.SERVER_SHORT }}/{{ c.SERVER_FULL }}`|{{ c.SERVER_HELP }} |
|`{{ c.LOGIN_PARAM }}`|`{{ c.LOGIN_SHORT }}/{{ c.LOGIN_FULL }}`|{{ c.LOGIN_HELP }}|
|`{{ c.PASSWORD_PARAM }}`|`{{ c.PASSWORD_SHORT }}/{{ c.PASSWORD_FULL }}`|{{ c.PASSWORD_HELP }} |

{% include 'admonitions/password_warning.md' %}


### Секция `jtl.defaults`

Секция общих параметров по умолчанию

|Параметр в конфиг. файле | Параметр командной строки |Описание      |
|----------|------------------|-------------------------|
|`{{ c.PROJECT_PARAM }}` |`{{ c.PROJECT_SHORT }}/{{ c.PROJECT_FULL }}`|{{ c.PROJECT_CONFIG_HELP }}|


### Секция `jtl.defaults.create-issue`

Секция параметров по умолчанию команды создания задачи

|{{ "Параметр в конфиг. файле" | wordwrap(15, wrapstring="<br/>") }} | {{ "Параметр командной строки" | wordwrap(17, wrapstring="<br/>") }}|Описание      |
|-----------------|------------------|----------------------------------|
|`{{ c.TEMPLATE_PARAM }}`|`{{ c.TEMPLATE_SHORT }}/{{ c.TEMPLATE_FULL }}`|{{ c.TEMPLATE_HELP }}|
|`{{ c.OPEN_LINK_PARAM }}`|`{{ c.OPEN_LINK_FULL }}`|{{ c.OPEN_LINK_CONFIG_HELP }}|
