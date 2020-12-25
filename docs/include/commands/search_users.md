## jtl search-users
    
    {{ get_command_usage("search-users") }}

{{ get_command_help("search-users") }}

### Параметры

| CLI | Config | Описание |
|-----|--------|----------|
{% for param in get_command_params("search-users") -%}
| `{{ get_param_opts(param) }}` | [{{ get_param_config(param) }}](configuration.md#формат-конфигурационного-файла) | {{ param.help }} |
{% endfor %}


Поиск конкретного пользователя в проекте DEV:

    $ jtl search-users -p DEV alek
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
