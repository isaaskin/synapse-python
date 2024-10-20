from logging import Logger
from typing import Union

from .adapters.adapter import Adapter

PAYLOAD = Union[str, int, float, dict]


class Connector:
    def __init__(self, adapter: Adapter, logger: Logger = Logger("Connector")) -> None:
        self._adapter = adapter
        self._logger = logger

    def run(self) -> None:
        raise NotImplementedError

    def stop(self) -> None:
        raise NotImplementedError
