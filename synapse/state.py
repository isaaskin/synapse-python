from typing import Any, Callable

from .event import Event


class State(Event):
    def __init__(self, initial_value: Any = None) -> None:
        super().__init__()
        self._value = initial_value

    def set(self, value: Any) -> None:
        if self._value == value:
            return
        self._value = value
        self.notify(self._value)

    def get(self) -> Any:
        return self._value

    def subscribe(self, callback: Callable[..., Any]) -> None:
        if self.get() is not None:
            callback(self.get())
        return super().subscribe(callback)
