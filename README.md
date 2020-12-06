# Инструмент автоматизации работы в Jira

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
* Активируйте виртуальное окружение
    ```
    poetry shell    
    ```
* Теперь можно вывести справку инструмента
    ```
    jira --help
    ```

## Функциональность


- [ ] Вспомогательные функции
    - [x] Создание issue из командной строки
    - [x] Функция поиска пользователя (для поля assignee)
    - [ ] Функция просмотра всех полей задачи (для поиска спринта вручную)
    - [ ] Функция поиска спринтов
- [ ] Групповое создание issue по шаблону в yaml
    - [x] Простой аналог JSON API создания Issue в Jira
    - [ ] Добавление подписи об автоматическом создании в description
    - [ ] Шаблонизирование строковых полей из указанных отдельно переменных
    - [ ] Создание вложенных наборов Issue
        - [ ] Наследование полей родительского Issue
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
- [ ] Возможность выгрузки Issue из Jira в yaml-файл
- [ ] Поддержка конфигурационных файлов (Jira url, login/password)
- [ ] Библиотека для создания собственных скриптов/сценариев автоматизации
- [ ] Логирование
    - [ ] Совершенных действий
    - [ ] Всех осуществленных запросов к Jira
- [ ] Транслятор из Markdown в Jira Text Formatting
