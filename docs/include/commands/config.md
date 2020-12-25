## jtl config init

    {{ get_command_usage("config", "init") }}

{{ get_command_help("config", "init") }}

### Параметры

| CLI |Prompt| Config | Описание |
|-----|------|--------|----------|
{% for param in get_command_params("config", "init") -%}
| `{{ get_param_opts(param) }}` |{{ get_param_prompt(param) }} | [{{ get_param_config(param) }}](configuration.md#формат-конфигурационного-файла) | {{ param.help }} |
{% endfor %}

{% include 'admonitions/prompt_note.md' %}


## jtl config set

    {{ get_command_usage("config", "set") }}

{{ get_command_help("config", "set") }}

### Параметры

| CLI | Config | Описание |
|-----|--------|----------|
{% for param in get_command_params("config", "set") -%}
| `{{ get_param_opts(param) }}` | [{{ get_param_config(param) }}](configuration.md#формат-конфигурационного-файла) | {{ param.help }} |
{% endfor %}
