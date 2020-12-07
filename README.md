# JTL (Jira TeamLead) Инструмент автоматизации создания задач в Jira

Позволяет автоматизировать создавать связанные наборы issue.
Например, если нужно создать комплексную задачу,
 в которой находятся подзадачи для разных ролей в команде.

## Установка и использование 

* Установите Python >= 3.6.1
* Установите poetry
* Клонируйте репозиторий
* Перейдите в основную директорию
* Установите зависимости и основное приложение
    ```
    poetry install
    ```
* Теперь можно вывести справку инструмента
    ```
    jtl --help
    ```
* Общие параметры всех команд можно передавать через переменные окружения или .env-файл:
    * `--server`: `JTL_SERVER`
    * `--auth`: `JTL_AUTH`

## Функциональность

- [ ] Вспомогательные функции
    - [x] Создание issue из командной строки
    - [x] Функция поиска пользователя (для поля assignee)
    - [ ] Функция просмотра всех полей задачи (для поиска спринта вручную)
    - [ ] Функция поиска спринтов
    - [ ] Команда для возврата Issue в формате `PROJ-111 Summary of Issue`
- [ ] Групповое создание issue из данных в yaml
    - [x] Простой аналог JSON API создания Issue в Jira
    - [ ] Общий шаблон для полей всех Issue в наборе
    - [ ] Добавление подписи об автоматическом создании в description
    - [ ] Шаблонизирование строковых полей из указанных отдельно переменных
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
- [x] Поддержка переменных окружения (jira host, credentials)
- [ ] Поддержка конфигурационных файлов (Jira url, login/password)
- [ ] Поддержка файлов cookie
- [ ] Логирование
    - [ ] Совершенных действий
    - [ ] Всех осуществленных запросов к Jira
- [ ] Опция `--dry-run`
- [ ] Транслятор из Markdown в Jira Text Formatting
