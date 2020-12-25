## jtl create-issue-set

    {{ get_command_usage("create-issue-set") }}

{{ get_command_help("create-issue-set") }}

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
