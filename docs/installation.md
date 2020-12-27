# Установка

## Системные требования

* [Python](https://www.python.org/) >= 3.6.1

## Варианты установки

### С использованием poetry

    $ poetry add jira_teamlead

### С использованием pip

    $ pip install jira_teamlead

### Из исходного кода

    $ git clone https://github.com/anegramotnov/jira-teamlead.git
    $ cd jira-teamlead
    $ poetry build
    $ pip install dist/jira-teamlead-0.1.0.tar.gz # or other version

### Для разработки

    $ git clone https://github.com/anegramotnov/jira-teamlead.git
    $ cd jira-teamlead
    $ poetry install  # with development dependencies!

## Включение автодополнения

Автодополнение существенно облегчает работу в jtl, так как работает,
в том числе, и для значений параметров с подгрузкой из Jira -- для значений
параметров `assignee`, issuetype`, `project` и т.п.

Для включения автодополнения, добавьте в `~/.bashrc` следующую строку:

    eval "$(_JTL_COMPLETE=source_bash jtl)"

Перезагрузите `~/.bashrc` для включения автодополнения в текущей сессии

    $ source ~/.bashrc

!!! tip "Подсказка"
    См. [справку по настройке автодополнения библиотеки Click](https://click.palletsprojects.com/en/7.x/bashcomplete/#activation)

