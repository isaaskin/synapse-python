import asyncio
import json
from typing import Awaitable, Callable

from .adapters import Adapter
from .connector import Connector
from .logger import Logger


class ConnectorServer(Connector):
    def __init__(
        self, adapter: Adapter, logger: Logger = Logger("ConnectorServer")
    ) -> None:
        super().__init__(adapter, logger)

        self.__commands: dict[str, Callable[[str], Awaitable[str]]] = dict()

    def __check_if_connected(self) -> bool:
        if not self._adapter.is_connected():
            self._logger.error("Adapter is not connected")
            return False
        return True

    async def publish_state(self, name: str, payload: str) -> None:
        if not self.__check_if_connected():
            return
        self._logger.debug("Publishing state [%s] with payload [%s]", name, payload)

        await self._adapter.publish(f"state/{name}", payload)

    async def publish_event(self, name: str, payload: str) -> None:
        if not self.__check_if_connected():
            return
        self._logger.debug("Publishing event [%s] with payload [%s]", name, payload)

        await self._adapter.publish(f"event/{name}", payload)

    def register_command(
        self, name: str, callback: Callable[[str], Awaitable[str]]
    ) -> None:
        self._logger.debug("Registering command [%s]", name)

        if name in self.__commands:
            self._logger.error("Command [%s] already registered", name)
            return

        async def process_command(message: str):
            self._logger.debug(
                "Processing command [%s] with message [%s]", name, message
            )
            message_dict = json.loads(message)

            if "payload" not in message_dict:
                self._logger.error("payload not in message")
                return

            if "correlation_id" not in message_dict:
                self._logger.error("correlation_id not in message")
                return

            response = await callback(message)

            response_to_be_sent = json.dumps(
                {"correlation_id": message_dict["correlation_id"], "payload": response}
            )
            await self._adapter.publish("command/response", response_to_be_sent)

        self._adapter.subscribe(f"command/{name}", process_command)

    def run(self) -> None:
        self._logger.info("Running connector server")

        try:
            asyncio.run(self._adapter.connect())
        except KeyboardInterrupt:
            print("Keyboard interrupt")
