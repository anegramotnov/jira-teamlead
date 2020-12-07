# JTL (Jira TeamLead) Инструмент автоматизации создания задач в Jira

Позволяет автоматизировать работу тимлида/техлида по созданию задач в Jira, если:

* Нужно очень быстро создать небольшую задачку -- для этого есть короткая
  консольная команда с возможностью шаблонизации с помощью yaml-файла любых
  полей задачи.
* Нужно создать много задач сразу -- для этого есть пакетное создание
  задач с использованием yaml-файла
* Нужно создать задачу с подзадачами без смещения фокуса внимания с
  декомпозици на рутинные действия в интерфейсе Jira -- для этого в пакетном
  создании задач есть функция добавления подзадач, наследующих поля
  родительской задачи и возможностью наглядно сконфигурировать связь между
  всеми задачами до их создания (связывание задач еще в разработке).
* Нужно отредактировать набор созданных задач (например, поправить
  продублированное название в подзадачах и основной задаче) -- но это еще не
  готово :)
* Хочется создавать задачи в строго фиксированном формате поля description (
  например, баг-репортов) -- но это кажется уже перебором.
  
Подробный список реализованных функций и планы по развитию находятся в разделе
Функциональность.

## Установка

* Установите Python >= 3.6.1
* Установите poetry
* Клонируйте репозиторий
* Перейдите в основную директорию
* Установите зависимости и основное приложение
    ```
    $ poetry install
    ```
* Теперь можно вывести справку инструмента
    ```
    $ jtl --help
    ```
* Возможна установка не только рамках виртуального окружения, но и глобально
  в систему с помощью команд:
  ```
  $ poetry build
  $ pip install dist/<path_to_build>
  ```

## Использование

### Основные принципы

* Главная цель jtl - облегчение рутинных действий по созданию задач в Jira,
  преимущественно, тимлида/техлида, т.е. человека с достаточной квалификацией
  для использования командной строки и редактирования YAML-файлов
* Все, что может быть шаблонизировано и параметризовано в создании задач,
  должно быть шаблонизировано и параметризовано.
* Основной формат для шаблонизаци - YAML, структуры данных в котором должны
  быть аналогичны со структурами данных в JSON-объектах, используемых в Jira
  REST API, т.е. не требовать дополнительной разработки, маппинга и документации.
  Документация для Jira REST API: https://docs.atlassian.com/software/jira/docs/api/REST/
* Для ускорения рутинных действий, исходны формат расширяется с помощью
  дополнительных полей, которые должны явно выделяться в структуре данных с
  помощью префикса `jtl_`
  

### Конфигурация сервера и учетных данных

Доступно 3 варианта передачи приложению сервера и учетных данных (те, что
выше -- приоритетнее при разрешении порядка использования):

* Параметрами командной строки (также, доступны сокращенные варианты `-s` и `-a`):
    ```
    $ jtl get-issue --server http://localhost:8080 --auth login:password DEV-11
    ...
    ```
* В переменных окружения:
    ```
    $ export JTL_SERVER=http://localhost:8080
    $ export JTL_AUTH=login:password
    $ jtl get-issue DEV-11
    ...
    ```
    ```
    $ JTL_SERVER=https://localhost:8080 JTL_AUTH=login:password jtl get-issue DEV-11
    ...
    ```
* С помощью .env-файла (должен быть в директории, откуда запускается jtl):
    ```
    $ cat .env
    JTL_SERVER=https://localhost:8080
    JTL_AUTH=login:password

    $ jtl get-issue DEV-11    
    ...
    ```

### Поиск пользователей

Для корректного заполнения поля assignee необходимо получить идентификатор
пользователя.

Поиск конкретного пользователя в проекте DEV:

```
$ jtl search-users -p DEV alex
alex (Alexey, alex@localhost)
```

Получение списка всех пользователей, для поля assignee в проекте DEV:

```
$ jtl search-users -p DEV
...
admin (Administrator, admin@localhost)
alex (Alexey, alex@localhost)
fred (Frederic, fred@localhost)
...
```


### Cоздание одного Issue

Простое создание Story в проекте DEV

```
$ jtl create-issue -p DEV -t Story -s "Добавить функцию создания задачи"
Created issue: http://localhost:8080/browse/DEV-11
```

Создание Story с помощью YAML-шаблона. Обязательные параметры могут быть
заданы в шаблоне. В данном примере в шаблоне переопределены `--project` и
`--type` с помощью `project.key` и `issuetype.name`, соотвественно. Формат
YAML-файла полность повторяет формат JSON-объекта передеваемый методу создания
задачи `POST /rest/api/2/issue` в Jira REST API.

```
$ cat issue.yaml
project:
  key: DEV
issuetype:
  name: Story

$ jtl create-issue -tmpl issue.yaml -s "Добавить функцию создания задачи"
Created issue: http://localhost:8080/browse/DEV-11
```

Путь к файлу шаблона может быть указан в переменных окружения или .env-файле
с помощью переменной `JTL_ISSUE_TEMPLATE`.

```
export JTL_ISSUE_TEMPLATE=issue.yaml
$ jtl create-issue -s "Добавить функцию создания задачи"
Created issue: http://localhost:8080/browse/DEV-11
```


### Вывод информации о созданной задаче

Выводится YAML-файл в формате, полностью повторяющем формат JSON-объекта, 
возвращаемого методом получения данных задачи
`GET /rest/api/2/issue/{issueIdOrKey}` в Jira REST API.

```
$ jtl get-issue DEV-11
...
created: 2020-12-07T03:51:53.185+0300
summary: Добавить функцию создания задачи
issuetype:
  description: ''
  id: '10001'
  name: Story
...
```

### Пакетное создание задач

```
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
```

Все поля в YAML-файле в формате, полностью повторяющем формат JSON-объекта, 
получаемого методом создания задачи `POST /rest/api/2/issue` в Jira REST API, 
кроме служебных полей с префиксом `jtl_`.

* `jtl_template` - шаблон для всех задач, указанных в YAML-файле. Задачи
  наследуют и переопределяют поля, указанные в шаблоне.
* `jtl_issues` - набор задач для создания в Jira.
* `jtl_sub_issues` - набор подзадачи основной задачи, указанной на верхнем
  уровне. Подзадачи наследуют и переопределяют поля, указанные в основной
  задаче



## Функциональность

- [ ] Вспомогательные функции
    - [x] Создание задачи из командной строки
    - [x] Шаблонизация создания задачи из командной строки
    - [x] Переопределение параметров командной строки в шаблоне
    - [x] Функция поиска пользователя (для поля assignee)
    - [x] Функция просмотра всех полей задачи (для поиска спринта вручную)
    - [ ] Функция поиска спринтов
    - [ ] Команда для получения задачи в формате `PROJ-111 Summary of Issue`
- [ ] Пакетное создание задачи из данных в yaml
    - [x] Простой аналог JSON API создания Issue в Jira
    - [x] Общий шаблон для полей всех Issue в наборе
    - [ ] Добавление подписи об автоматическом создании в description
    - [ ] Шаблонизирование строковых полей из указанных отдельно переменных
    - [ ] Специальное поле для префикса в summary Sub-Issues
    - [ ] Создание вложенных наборов Issue
        - [x] Наследование полей родительского Issue
        - [ ] Шаблонизирование строковых полей строками родительского Issue
        - [ ] Автоматическая подстановка связей с родительской Issue
        - [ ] Автоматическая подстановка связей между вложенными Issue (порядок выполнения)
    - [ ] Возможнось не указывать конкретный идентификатор поля (id, name, key, и т.д.)
    - [ ] Генерация выходного файла с добавлением Issue Key
    - [ ] Редактирование выходного файла с последующей синхронизацией с Jira
    - [ ] Предварительная проверка валидности указанных полей (существование в Jira)
    - [ ] Подсказки корректных вариантов для невалидных полей
    - [ ] Откат операции при возникновении ошибки
    - [ ] Вывод подтверждения со списком действий перед выполнением команды
- [ ] Валидация по Json-schema REST API Jira
- [ ] Возможность выгрузки Issue из Jira в yaml-файл
- [x] Поддержка конфигурации в переменных окружения
- [ ] Поддержка конфигурационных файлов
- [ ] Поддержка сохранения cookie между вызовами
- [ ] Логирование
    - [ ] Совершенных действий
    - [ ] Всех осуществленных запросов к Jira
- [ ] Опция `--dry-run`
- [ ] Транслятор из Markdown в Jira Text Formatting
- [ ] Система плагинов (например, для расширения приложения командой
      заведения бага с шагами воспроизведения, ОР, ФР)
