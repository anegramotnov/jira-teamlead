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

### С использованием pip

    $ pip install jira_teamlead
      
### Из исходного кода

    $ git clone https://github.com/anegramotnov/jira-teamlead.git
    $ cd jira-teamlead
    $ poetry build
    $ pip install dist/jira-teamlead-0.1.0.tar.gz # or other version
    $ jtl --help  # usage

### Для разработки

    $ git clone https://github.com/anegramotnov/jira-teamlead.git
    $ cd jira-teamlead
    $ poetry install  # with development dependencies!
    $ # run using poetry:
    $ poetry run jtl --help
    $ # or run directly in venv
    $ poetry shell
    $ jtl --help

### Включение автодополнения (опционально)

Автодополнение существенно облегчает работу в jtl, так как кроме дополнения
вложенных команд или названий опций командной строки, работает для параметров,
относящихся к данным Jira -- значения опций `assignee`,
`issuetype` (в разработке), `sprint` (в разработке) и т.п.

Для включения автодополнения, добавьте в `~/.bashrc` следующую строку:

    eval "$(_JTL_COMPLETE=source_bash jtl)"
  
Перезагрузите `~/.bashrc` для включения автодополнения в текущей сессии

    $ source ~/.bashrc 
  
  > См. справку по настройке автодополнения библиотеки Click
  https://click.palletsprojects.com/en/7.x/bashcomplete/#activation


## Конфигурация

Конфигурация приложения может быть задана через конфигурационные файлы и
через параметры командной строки

### Порядок поиска параметров конфигурации

Указаны в порядке от высшего приоритета к низшему:

* Параметры командной строки
* Текущий конфигурационный файл
    * Файл, указанный в параметре `-cfg/--config`
    * Файл `.jtl.cfg`, находящийся в текущей директории
    * Файл `~/.jtl.cfg`, находящийся в домашней директории пользователя

> При отсутствии обязательного параметра в опциях командной строки и
  в конфигурационных файлах, он будет предложен для ввода (prompt-ввод) после
  запуска команды

### Формат конфигурационного файла

    [jtl.jira]
    server = http://localhost:8080
    login = my_login
    password = my_password
    
    [jtl.defaults]
    project = DEV
    
    [jtl.defaults.create-issue]
    template = default_issue.yaml

### Секции конфигурационного файла

#### `[jtl.jira]`

Секция подключения к серверу Jira:

|Config    |CLI               |Required|Описание      |
|----------|------------------|--------|--------------|
|`server`  |`-js / --server`  | +      |Сервера Jira  |
|`login`   |`-jl / --login`   | +      |Логин в Jira  |
|`password`|`-jp / --password`| +      |Пароль в Jira |

> __Поле `password` хранится в открытом виде!__ Во избежание риска
  компрометации, можно использовать для `password` prompt-ввод.

#### `[jtl.defaults]`

Секция общих параметров по умолчанию

|Config    |CLI               |Required|Описание                 |
|----------|------------------|--------|-------------------------|
|`project` |`-p / --project`  | -      |Ключ проекта по умолчанию|


#### `[jtl.defaults.create-issue]`

Секция параметров по умолчанию команды создания задачи

|Config    |CLI               |Required|Описание           |
|----------|------------------|--------|-------------------|
|`template`|`-tl / --template`| -      |Шаблон полей задачи|


### Примеры вариантов конфигурации

Без опций командной строки:

    $ jtl search-users
    Server: <prompt_typing>
    Login: <prompt_typing>
    Password: <hidden_prompt_typing>
    Project: <prompt_typing>
    ...

С опциями командной строки:

    $ jtl search-users --server http://localhost:8080 --login my_login \
    --password my_password --project DEV
    ...
    
С сокращенными опциями:
    
    $ jtl search-users -js http://localhost:8080 -jl my_login -jp my_password -p DEV
    ...
    
С конфигурационным файлом
    
    cat ~/.cfg
    [jtl.jira]
    server = http://localhost:8080
    login = my_login
    password = my_password
    
    $ jtl search-users -p DEV
    ...

## Команды

### Общие опции

|CLI               |Config               |Required|Описание             |
|------------------|---------------------|--------|---------------------|
|`-jc / --config`  | -                   | -      |Конфигурационный файл|
|`-js / --server`  |`[jtl.jira] server`  | +      |Сервера Jira         |
|`-jl / --login`   |`[jtl.jira] login`   | +      |Логин в Jira         |
|`-jp / --password`|`[jtl.jira] password`| +      |Пароль в Jira        |


### get-assignee

Вывод списка пользователей, доступных для поля `assignee`

Поиск конкретного пользователя в проекте DEV:

    $ jtl get-assignee -p DEV alek
    aleksey.alekseev (Aleksey Alekseev, aleks@localhost)
    #
    # assignee.name   a.displayName     a.emailAddress

Получение списка всех пользователей в проекте DEV:

    $ jtl search-users -p DEV
    ...
    admin (Administrator, admin@localhost)
    aleksey.alekseev (Aleksey Alekseev, alex@localhost)
    andrey.andreev (Andrey Andreev, andrey@localhost)
    ...

#### Опции

|CLI               |Config                  |Required|Описание  |
|------------------|------------------------|--------|----------|
|`-p / --project`  |`[jtl.defaults] project`| +      |ID проекта|


### create-issue

Создание задачи

Простое создание Story

    $ jtl create-issue -t Story -s "Добавить команду создания задач"
    Created issue: http://localhost:8080/browse/DEV-123

Поля задачи могут быть заданы в шаблоне
    
    $ cat issue.yaml
    labels:
      - MyBeautifulTeam
    issuetype:
      name: "Story"
    
    $ jtl create-issue -jt issue.yaml -s "Добавить команду создания задач"
    Created issue: http://localhost:8080/browse/DEV-123
    
    $ jtl get-issue DEV-123
    ...
    summary: Добавить команду создания задач
    ...
    issutype:
      ...
      - name: Story
      ...
    labels:
      - MyBeautifulTeam
    ...

> Структура YAML-шаблона соответствуют структуре поля `issues` JSON-объекта,
  отправляемого теле метода `POST /rest/api/2/issue` в Jira REST API за
  исключением служебных полей с префиксом `jtl_`. Cм. документацию к Jira
  REST API https://docs.atlassian.com/software/jira/docs/api/REST/

> Доступно автодополнение поля `-a / --assignee`.
  См. [Включение автодополнения в bash](#включение-автодополнения-в-bash)

Путь к файлу шаблона может быть указан в конфигурационном файле

    $ cat ~/.jtl.cfg
    [jtl.defaults.create-issue]
    template = issue.yaml
    
    $ jtl create-issue -s "Добавить функцию создания задачи"
    Created issue: http://localhost:8080/browse/DEV-123

#### Опции

|CLI               |Config                                |Template        |Required|Описание           |
|------------------|--------------------------------------|----------------|--------|-------------------|
|`-jt / --template`|`[jtl.defaults.create-issue] template`|                | -      |Шаблон полей задачи|
|`-p / --project`  |`[jtl.defaults] project`              |`project.key`   | +      |ID проекта         |
|`-t / --type`     | -                                    |`issuetype.name`| +      |Тип задачи         |
|`-a / --assignee` | -                                    |`assignee.name` | -      |Исполнитель задачи |
|`-s / --summary`  | -                                    |`summary`       | +      |Поле задачи "Тема" |


### get-issue

Вывод информации о созданной задаче

Выводится YAML-файл в формате, который полностью соответствует формату
JSON-объекта,возвращаемого методом получения данных задачи
`GET /rest/api/2/issue/{issueIdOrKey}` в Jira REST API. Cм. документацию к
Jira REST API https://docs.atlassian.com/software/jira/docs/api/REST/

    $ jtl get-issue DEV-11
    ...
    created: 2020-12-07T03:51:53.185+0300
    summary: Добавить функцию создания задачи
    issuetype:
      description: ''
      id: '10001'
      name: Story
    ...

### create-issue-set

Пакетное создание задач

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

## Описание полей задачи

* Поле спринта. Имеет формат `customfield_10101`, но цифры на разных Jira-серверах
  отличаются. В ответе сервера содержимое поля приходит примерно таким:
  `"com.atlassian.greenhopper.service.sprint.Sprint@6cd8e5ef[id=55,rapidViewId=40,state=ACTIVE,name=...`,
  где id=55 - это идентификатор спринта. В запросе на создание задачи можно
  передавать просто идентификатор спринта: `customfield_10101: 55`.

## Устранение неполадок

* Если в Git Bash при выводе `--help` не отображается кириллица, необходимо
либо запускать через winpty: `$ winpty jtl ...`, либо установить Git Bash с
включенной опцией "Enable experimental support for pseudo consoles."

## Дорожная карта

- Команды
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
- Шаблонизация задач
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
- Вспомогательные функции
    - [x] prompt для обязательных опций
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
- [ ] Идеи
    - [ ] Перенести общие опции CLI к основной команде?
    - [ ] Опция открытия созданных задач в браузере (с настройкой)
    - [ ] Убрать логику подстановки префикса `jtl.` в секции конфигов
    - [ ] Убрать сокращенный вариант опций конфигурационных параметров
    - [ ] Добавить в команду create-issue параметр для создания сабтасок с
      префиксами для summary оригинальной задачи
    - [ ] Убрать из issue_set.yaml поле шаблона и использовать общий шаблон из
      create-issue
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
    - [ ] Опция `--filter` для `get-issue` для поиска по имени ветки, т.к.
      grep в mintty не работает с юникодом. 
- [ ] Технический долг
    - [ ] Вынести все параметры опций в dict
    - [ ] Отрефакторить пакет cli - пенести комманды в соответствующие пакеты
      `commands.<entity>.<concrete_command>`, опции в `options`
    - [x] Отрефакторить извлечение опции из конфига. Есть более удачный способ
      с подменой `cls=CustomOption`, использованный в извлечении параметра из
      шаблона. Используемый сейчас `callback=` задумывался для другого -
      для окончательной обработки значения перед передачей в команду. Также,
      это позволит избавиться от кастомного флага `required=`. Кроме того,
      неизвестно, какие проблемы еще несет текущая реализация. Осталось
      придумать, что делать с логикой, которая рендерит другое сообщение об
      ошибке, если параметр был взят из конфига.
    - [x] Не выводить [required] для FallbackOption
    - [ ] Заменить повсеместное использование `callback=` на `type=`. Сейчас
      все `callback=` делают именно то, что должен делать `type=`.
    - [ ] Магия `@add_jira_options` и `@add_config_option`/`@remove_config_option`
      не применяется для `ctx.params` в аргументах функции обратного вызова
      `autocompletion=`. Понять, почему и придумать, как исправить.
    - [x] Разделить `jira-auth` на `jira-login` и `jira-password`
    - [ ] Сделать `jira-password` вводимым из prompt
