"""
The event module contains the Event class, which is used to implement
a publish-subscribe pattern.
"""
from typing import Any, Callable


class Event:
    """Event class.

    This class is used to create a publish-subscribe system.
    """

    def __init__(self) -> None:
        """Initialize the event."""
        self._observers = set()

    def subscribe(self, callback: Callable[..., Any]) -> None:
        """Subscribe to the event."""
        self._observers.add(callback)

    def unsubscribe(self, callback: Callable[..., Any]) -> None:
        """Unsubscribe from the event."""
        self._observers.remove(callback)

    def notify(self, data) -> None:
        """Notify all observers."""
        for observer in self._observers:
            observer(data)
