from jira_teamlead.cli import jtl

if __name__ == "__main__":
    module_command_path = "python -m {0}".format(__package__)
    jtl(prog_name=module_command_path)
