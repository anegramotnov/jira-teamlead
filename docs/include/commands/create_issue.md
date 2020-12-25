## jtl create-issue

    {{ get_command_usage("create-issue") }}

{{ get_command_help("create-issue") }}

### Параметры

| Параметр | {{ 'Путь в шаблоне' | wordwrap(7, wrapstring='<br/>') }} | {{ "Параметр в конфиг. файле" | wordwrap(9, wrapstring="<br/>") }}|Обя-<br/>зате-<br/>льный| Описание |
|-----|----------|--------|---------|----------|
{% for param in get_command_params("create-issue") -%}
|`{{ get_param_opts(param) }}`|`{{ get_template_query(param) }}`| [{{ get_param_config(param) }} ](configuration.md#формат-конфигурационного-файла)|{{ get_param_required(param) }}|{{ param.help | wordwrap(23, wrapstring='<br/>') }}|
{% endfor %}

{% include 'admonitions/autocompletion_note.md' %}

### Порядок поиска значений параметров

Порядок поиска значений параметров (выше - более приоритетные)

* Параметры командной строки
* Шаблон
* Конфигурационный файл (см. 
  [Порядок поиска параметров источников конфигурации](configuration.md#порядок-поиска-источников-конфигурации))
* Запрос у пользователя (prompt-ввод). Только для обязательных параметров.

Это означает, что при отсутствии переданного значения параметра командной
строки, будет происходить поиск значения в шаблоне  (если был передан параметр 
`-tl/--template` или установлен параметр `issue_template` в конфигурационном
файле). В столбце "Путь в шаблоне" [таблицы параметров](#параметры_2)
указан путь в структуре шаблона, по которому будет происходить поиск параметра.

Например, путь `assignee.name` извлечет из следующего шаблона значение
`aleksey.alekseev`:

    project:
      key: DEV
    assignee:
      name: aleksey.alekseev

Далее, при отсутствии параметра в шаблоне, будет произведен поиск
параметра в конфигурационном файле. В столбце "Параметр в конфиг. файле"
приведено название конфигурационного параметра без указания секции.
Подробнее см. в разделе
[Формат конфигурационного файла](configuration.md#формат-конфигурационного-файла)

Далее, при отсутствии параметра в конфигурационном файле, он будет
предложен для ввода после запуска команды (prompt-ввод), если параметр
является обязательным.


### Примеры

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



Путь к файлу шаблона может быть указан в конфигурационном файле

    $ cat ~/.jtl.cfg
    [jtl.defaults.create-issue]
    template = issue.yaml

    $ jtl create-issue -s "Добавить функцию создания задачи"
    Created issue: http://localhost:8080/browse/DEV-123
