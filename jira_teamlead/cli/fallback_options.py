from typing import Any, Callable, List, Optional

import click


class FallbackOption(click.Option):
    """Опция, которая при отсутствии параметра CLI, извлекает значение из других мест.

    Attributes:
        fallbacks: Список коллбэков для попытки извлечения значения, выполняются по
            порядку.
        fallback_hint: Строка, отображаемая в сообщениях об ошибках, связанных с
            параметром. Должна быть присвоена оъекту в функции fallback для дальнейшей
            передачи в `click.BadParameter(..., param_hint)`.

    """

    fallbacks: List[Callable]
    fallback_hint: Optional[str] = None

    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        fallback = kwargs.pop("fallback")
        self.fallbacks = [fallback] if not isinstance(fallback, list) else fallback

        super().__init__(*args, **kwargs)

    def consume_value(self, ctx: click.Context, opts: dict) -> Any:
        value = opts.get(self.name)
        if value is None:
            value = self.value_from_envvar(ctx)
        if value is None:
            for fallback in self.fallbacks:
                value = fallback(ctx=ctx, param=self)
                if value is not None:
                    break
        if value is None:
            value = ctx.lookup_default(self.name)
        return value

    def handle_parse_result(self, ctx: click.Context, opts: dict, args: list) -> Any:
        try:
            return super().handle_parse_result(ctx, opts, args)
        except click.BadParameter as e:
            if self.fallback_hint is not None:
                e.param_hint = self.fallback_hint
            raise
