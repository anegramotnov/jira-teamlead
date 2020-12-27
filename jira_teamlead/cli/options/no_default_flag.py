from typing import Optional

import click


class NoDefaultFlagOption(click.Option):
    """Опция, отключающая дефолтное значение для флагов."""

    def get_default(self, ctx: click.Context) -> None:
        """Никогда не использовать значение default."""
        return None

    def get_error_hint(self, ctx: Optional[click.Context]) -> str:
        """Добавить в сообщение об ошибке 'обратный' флаг из secondary_opts."""
        error_opts = self.opts + self.secondary_opts
        hint_list = error_opts or [self.human_readable_name]
        return " / ".join(repr(x) for x in hint_list)
