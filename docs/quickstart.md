# Быстрый старт

## Подготовте директорию для работы с проектом в Jira
    
Создайте директорию для хранения настроек подключения к экземпляру Jira,
файлов конфигурации, шаблонов создания задачи и файлов с наборами задач
    
    $ mkdir project_dev
    $ cd project_dev

## Создайте базовую конфигурацию

Введите команду инициализации конфигурационного конфига с единственным
параметром `--local` (создание конфигурационного файла в текущей директории).

    $ jtl config init --local

{% include "admonitions/prompt_note.md" %}
    

!!! tip "Подсказка"
    См. подробную справку команды [jtl config init](commands.md#jtl-config-init)

{% include 'admonitions/password_warning.md' %}

## Создайте первую задачу

С помощью задания обязательных опций вручную

    $ jtl create-issue --type Task --summary "My First Task"
    
В сокращенном виде
    
    $ jtl create-issue --t Task --s "My First Task"
    
Или без опций (обязательные будут запрошены после запуска командой)

    $ jtl create-issue

!!! tip "Подсказка"
    См. подробную справку команды [jtl create-issue](commands.md#jtl-create-issue)


## Добавьте шаблон для создания задачи

Создайте файл yaml-шаблон создания задачи со следующим содержимым
    
    # issue_template.yaml
    issuetype:
      name: Task
      
{% include "admonitions/issue_yaml_note.md" %}

Теперь можно не указывать тип задачи при создании, если указать шаблон в
опциях командной строки
    
    $ jtl create-issue --template issue_template.yaml --summary "My First Templated Task"
    
!!! tip "Подсказка"
    См. подробную справку команды [jtl create-issue](commands.md#jtl-create-issue)

## Добавьте yaml-шаблон создания задачи в настройки

    $ jtl config set --template issue_template.yaml

!!! tip "Подсказка"
    См. подробную справку команды [jtl config set](commands.md#jtl-config-set)

Или добавив вручную конфигурационный параметр в `.jtl.cfg` в текущей директории 
    
    $ cat .jtl.cfg
    ...
    [jtl.defaults.create-issue]
    issue_template = issue_template.yaml
    ...

Теперь можно создавать задачи без указания опции `-t / --type`

    $ jtl create-issue -s "My First Templated Task"
    
## Укажите исполнителя задачи

Выведите список всех пользователей, доступных для назначения задач

    $ jtl search-users
    ...
    alekey.alekseev (Aleksey Alekseev, aleksey.alekseev@domain.net)
    andrey.andreev (Andrey Andreev, andreay.andreev@domain.net)
    ...

Или укажите фильтр для поиска

    $ jtl search-users alek
    alekey.alekseev (Aleksey Alekseev, aleksey.alekseev@domain.net)

!!! tip "Подсказка"
    См. подробную справку команды [jtl search-users](commands.md#jtl-search-users)


Теперь можно указать исполнителя задачи

    $ jtl create-issue -a aleksey.alekseev -s "My First Assignable Task"

Можно воспользоваться автодополнением по полю `assignee`

    $ jtl create-issue -a alek<TAB><TAB>sey.alekseev

{% include 'admonitions/autocompletion_note.md' %}

## Попробуйте расширить шаблон дополнительными полями

Получите данные существующей задачи в YAML-формате:

    $ jtl get-issue DEV-11
    ...
    created: 2020-12-07T03:51:53.185+0300
    summary: My First Assignable Task
    issuetype:
      description: ''
      id: '10001'
      name: Story
    ...
