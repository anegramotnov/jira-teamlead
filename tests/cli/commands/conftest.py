import pytest
from click.testing import CliRunner


@pytest.fixture()
def cli():
    runner = CliRunner()
    with runner.isolated_filesystem():
        yield runner
