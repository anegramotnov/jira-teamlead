from functools import update_wrapper
from typing import Any, Callable, List


def skip_parameter(name: str, silent: bool = True) -> Callable:
    def decorator(f: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                kwargs.pop(name)
            except KeyError:
                if not silent:
                    raise
            return f(*args, **kwargs)

        return update_wrapper(wrapper, f)

    return decorator


def aggregate_parameters(
    name: str,
    params: List[str],
    callback: Callable,
) -> Any:
    def decorator(f: Callable) -> Callable:
        def wrapper(**kwargs: Any) -> Any:
            param_dict = {}
            for param in params:
                param_value = kwargs.pop(param)

                param_dict[param] = param_value

            value = callback(**param_dict)
            kwargs[name] = value
            return f(**kwargs)

        return update_wrapper(wrapper, f)

    return decorator
