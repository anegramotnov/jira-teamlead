# JTL (Jira TeamLead) Инструмент автоматизации создания задач в Jira

Позволяет тимлиду/техлиду автоматизировать рутинные операции по созданию задач
в Jira:

* Быстрое создание небольшой задачи с возможностью шаблонизации полей в YAML-файле.
* Пакетное создание задач из YAML-файа
* Создание задачи со списком подзадач, с наследованием родительских полей и
  возможностью описать связей между подзадачами (связи между задачами в разработке).
* Пакетное редактирование в YAML ранее созданных задач (в разработке). 
* Создание задачи с фиксированным форматом description, например -- багрепорта
  (в разработке).

Подробный список функций и планы по развитию находятся в разделе
[Дорожная карта](#Дорожная-карта).

## Основные принципы

* Максимальное использование шаблонов задач для обеспечения возможности
  вводить только значимые данные при создании задач
* Шаблоны задач в формате YAML
* Структура объектов в YAML-шаблонах задач полностью соответствуют структуре
  объектов JSON в REST API Jira, за исключением служебных полей с префиксом `jtl_` 
* Служебные поля с префиксом `jtl_` отвечают за дополнительную логику
  обработки шаблона

## Системные требования

* [Python](https://www.python.org/) >= 3.6.1

## Установка

* Установите пакет

      $ pip install jira_teamlead

* Теперь можно запускать jtl из командной строки

      $ jtl --help

* [Опционально] Для включения автодополнения, добавьте в `~/.bashrc`
  следующую команду:

      eval "$(_JTL_COMPLETE=source_bash jtl)"
  
  Перезагрузите `~/.bashrc` для включения автодополнения в текущей сессии

      $ source ~/.bashrc 
  
  > См. справку по настройке автодополнения библиотеки Click
  https://click.palletsprojects.com/en/7.x/bashcomplete/#activation

## Конфигурация

### Общие конфгигурационные параметры

|CLI                    |Config  |Required|Описание                                          |
|---------------------|--------|--------|----------------------------------------------------|
|`-cfg / --config`    | -      | -      |Путь к конфигурационному файлу                      |
|`-ja / --jira-auth`  |`auth`  | +      |Логин и пароль в формате `login:password`           |
|`-js / --jira-server`|`server`| +      |URL сервера Jira в формате `http[s]://jira.host.net`|

#### Примеры:

Использование конфигурационного файла:

    $ cat my_config.cfg
    [jtl]
    server = http://localhost:8080
    auth = login:password
    $ jtl get-issue --config my_config.cfg DEV-11

Использование параметров командной строки:

    $ jtl get-issue --jira-server http://localhost:8080 --jira-auth login:password DEV-11

#### Порядок поиска параметров конфигурации

Указаны в порядке от высшего приоритета к низшему:

* Параметры командной строки
* Файл, указанный в параметре `-cfg/--config`
* Файл `.jtl.cfg`, находящийся в текущей директории
* Файл `~/.jtl.cfg`, находящийся в домашней директории пользователя

#### Формат конфигурационного файла

    [jtl.jira]
    server = http://localhost:8080
    auth = login:password
    
    [jtl.create-issue]
    template = default_issue.yaml
    
    [jtl.other-command]
    ...

Конфигурационный файл делится на секции:

##### `[jtl.jira]` 

Секция общих конфигурации сервера Jira. См. раздел
[Общие конфгигурационные параметры](#Общие-конфгигурационные-параметры)

##### `[jtl.<command-name>]`

Секции параметров команды `<command-name>`. См. документацию к
`<command-name>`

## Команды

#### Поиск пользователей

Служит для поиска логина пользователей, которые можно потом использовать в
качестве идентификаторов для поля assignee.

Поиск конкретного пользователя в проекте DEV:

    $ jtl search-users -p DEV alex
    alex (Alexey, alex@localhost)

Получение списка всех пользователей, для поля assignee в проекте DEV:

    $ jtl search-users -p DEV
    ...
    admin (Administrator, admin@localhost)
    alex (Alexey, alex@localhost)
    fred (Frederic, fred@localhost)
    ...

#### Создание одной задачи

##### Примеры

Простое создание Story в проекте DEV

    $ jtl create-issue -p DEV -t Story -s "Добавить функцию создания задачи"
    Created issue: http://localhost:8080/browse/DEV-11

Обязательные параметры могут быть заданы в шаблоне (например, `--project` и
`--type`):

    $ cat issue.yaml
    project:
      key: DEV
    issuetype:
      name: Story
    
    $ jtl create-issue -tmpl issue.yaml -s "Добавить функцию создания задачи"
    Created issue: http://localhost:8080/browse/DEV-11

> Структура объектов полностью соответствуют структуре объектов JSON в REST
  API Jira, за исключением служебных полей с префиксом `jtl_`.

> Доступно автодополнение поля `-a / --assignee`.
  См. [Включение автодополнения в bash](#включение-автодополнения-в-bash)

Путь к файлу шаблона может быть указан в конфигурационном файле

    $ cat ~/.jtl.cfg
    [jtl.create-issue]
    issue_template = issue.yaml
    
    $ jtl create-issue -s "Добавить функцию создания задачи"
    Created issue: http://localhost:8080/browse/DEV-11

TODO: Добавить пример с многострочным description

#### Вывод информации о созданной задаче


Выводится YAML-файл в формате, полностью cоответствующем формату JSON-объекта, 
возвращаемого методом получения данных задачи
`GET /rest/api/2/issue/{issueIdOrKey}` в Jira REST API.

    $ jtl get-issue DEV-11
    ...
    created: 2020-12-07T03:51:53.185+0300
    summary: Добавить функцию создания задачи
    issuetype:
      description: ''
      id: '10001'
      name: Story
    ...

#### Пакетное создание задач

    $ cat issues.yaml
    jtl_template:
      project:
        key: "DEV"
      labels:
        - "dreamteam"
        - "refactoring"
      customfield_10104: 1    # Sprint value
    jtl_issues:
      - summary: "Refactoring the issue creation function"
        description: "Very detailed description..."
        issuetype:
          name: Story
        assignee:
          name: "admin"
        jtl_sub_issues:
          - summary: "[Frontend] Refactoring the issue creation function"
            issuetype:
              name: Task
            assignee:
              name: "frontend.developer"
          - summary: "[Backend] Refactoring the issue creation function"
            issuetype:
              name: Task
            assignee:
              name: "frontend.developer"
    
    $ jtl create-issue-set issues.yaml
    Created super-issue: http://localhost:8080/browse/DEV-13
        Created sub-issue: http://localhost:8080/browse/DEV-14
        Created sub-issue: http://localhost:8080/browse/DEV-15

> Структура объектов в YAML полностью соответствуют структуре объектов JSON в
  REST API Jira, за исключением служебных полей с префиксом `jtl_`.

* `jtl_template` - шаблон для всех задач, указанных в YAML-файле. Задачи
  наследуют и переопределяют поля, указанные в шаблоне.
* `jtl_issues` - набор задач для создания в Jira.
* `jtl_sub_issues` - набор подзадачи основной задачи, указанной на верхнем
  уровне. Подзадачи наследуют и переопределяют поля, указанные в основной
  задаче

## Описание полей задачи

* `fields.assignee`: см. команду [Поиск пользователей](#Поиск-пользователей).
* Поле спринта. Имеет формат `customfield_10101`, но цифры на разных Jira-серверах
  отличаются. В ответе сервера содержимое поля приходит примерно таким:
  `"com.atlassian.greenhopper.service.sprint.Sprint@6cd8e5ef[id=55,rapidViewId=40,state=ACTIVE,name=...`,
  где id=55 - это идентификатор спринта. В запросе на создание задачи можно
  передавать просто идентификатор спринта: `customfield_10101: 55`.

## Дорожная карта

- [ ] Команды
    - [x] Создание задачи из командной строки
        - Параметры
            - [x] summary
            - [x] description
            - [x] assignee
                - [x] автодополнение
                - [ ] "Назначить на меня"
            - [x] Проект
                - [ ] Автодополнение
                - [x] Дефолтный из настроек
            - [ ] Спринт
                - [ ] Автодополнение
                - [ ] Активный спринт
                - [ ] Дефолтный из настроек
    - [x] Поиск пользователей (для поля assignee)
        - Параметры
            - [x] Проект
                - [ ] Автодополнение
                - [x] Дефолтный из настроек
    - [x] Просмотра всех полей задачи (например, для поиска спринта вручную)
    - [ ] Поиск спринтов
    - [ ] Пакетное создание задач из данных в yaml
    - [ ] Редактирование выходного файла с последующей синхронизацией с Jira
    - [ ] Команда login
    - [ ] Команда первоначальной конфигурации
    - [ ] Команда настройки автодополнения
    - [ ] Команда поиска поля спринта
- [ ] Шаблонизация задач
    - [x] Простая шаблонизация через YAML
    - [x] YAML-структуры соответствуют JSON структурам Jira REST API
    - [x] Создание вложенных наборов задач
    - [x] Наследование полей родительской задачи
    - [ ] Шаблонизирование строковых полей строками родительской задачи
    - [ ] Автоматическая подстановка связей с родительской задачей
    - [ ] Автоматическая подстановка связей между вложенными задачами
          (порядок выполнения)
    - [ ] Возможность указания связи через временные идентификаторы задач
    - [ ] Шаблонизирование строковых полей по переменным
    - [ ] Поле prefix для summary задачи
    - [ ] Cоздание задач из csv, шаблонизированных через YAML
    - [x] Заполнение пропущенных параметров из шаблонов
- [ ] Вспомогательные функции
    - [ ] Корректный рендеринг ошибок
    - [ ] Предварительная проверка валидности указанных полей (существование в Jira)
    - [ ] Подсказки вариантов для невалидных полей
    - [ ] Откат операции при возникновении ошибки (невозможно без административных прав)
    - [ ] Вывод подтверждения со списком действий перед выполнением команды
    - [x] Конфигурационные файлы
        - [x] Поддержка .ini
        - [x] Конфиги
            - [x] Локальный
            - [x] Пользовательский
            - [x] Из параметров CLI
        - [x] Настройки
            - [x] Данные для подключения к серверу (конфиги->параметры)
            - [x] Файл шаблона (конфиги->параметры)
            - [ ] Проект по умолчанию (конфиги->шаблон->параметры)
            - [ ] Спринт по умолчанию
        - [x] Подгрузка пропущенных параметров CLI из конфигов
    - [ ] Поддержка сохранения авторизации в файлах cookie
    - [ ] Логирование
        - [ ] Совершенных действий
        - [ ] Всех осуществленных запросов к Jira
    - [ ] Автодополнение в командной строке
        - [x] Субкомманд
        - [ ] Параметров (issuetype, sprint, assignee, project, etc)
            - [ ] Кеширование
    - [ ] Опция `--dry-run`
- [ ] Прочие идеи
    - [ ] Полную форму параметры приблизить к REST API (
      `project -> project.name`, `type -> issuetype.name`,
      `assignee -> assignee.name`)
    - [ ] Получения задачи в формате `PROJ-111 Summary of Issue`
    - [ ] Добавление подписи об автоматическом создании задачи в description
    - [ ] Подгрузка шаблонов задач из Jira, как в плагине Issue Templates for Jira
    - [ ] Система плагинов (например, для расширения приложения командой
      заведения бага с шагами воспроизведения, ОР, ФР)
    - [ ] Защита от повторного создания задач (с выводом подтверждения)
    - [ ] Разобраться с тем, как добавлять многострочный description
    - [ ] Переименовать template -> prototype (proto)
- [ ] Технический долг
    - [ ] Отрефакторить извлечение опции из конфига. Есть более удачный способ
      с подменой `cls=CustomOption`, использованный в извлечении параметра из
      шаблона. Используемый сейчас `callback=` задумывался для другого -
      для окончательной обработки значения перед передачей в команду. Также,
      это позволит избавиться от кастомного флага `required=`. Кроме того,
      неизвестно, какие проблемы еще несет текущая реализация. Осталось
      придумать, что делать с логикой, которая рендерит другое сообщение об
      ошибке, если параметр был взят из конфига.
    - [ ] Заменить повсеместное использование `callback=` на `type=`. Сейчас
      все `callback=` делают именно то, что должен делать `type=`.
    - [ ] Магия `@add_jira_options` и `@add_config_option`/`@remove_config_option`
      не применяется для `ctx.params` в аргументах функции обратного вызова
      `autocompletion=`. Понять, почему и придумать, как исправить.
    - [ ] Разделить `jira-auth` на `jira-login` и `jira-password`
    - [ ] Сделать `jira-password` вводимым из prompt
