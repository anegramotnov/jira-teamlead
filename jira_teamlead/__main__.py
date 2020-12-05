import click


@click.group()
def cli() -> None:
    """Инструмент автоматизации работы в Jira."""


@cli.command()
def create_issue() -> None:
    click.echo("Hello, Jira!")


if __name__ == "__main__":
    cli()
