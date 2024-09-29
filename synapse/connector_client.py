import asyncio
import json
from typing import Callable, Coroutine

from .adapters import Adapter
from .connector import Connector
from .logger import Logger


class ConnectorClient(Connector):
    def __init__(
        self, adapter: Adapter, logger: Logger = Logger("ConnectorClient")
    ) -> None:
        super().__init__(adapter, logger)

        self.__command_correlation_id = 0

        # Command responses
        self._adapter.subscribe("command/response", self.__on_command_response)
        self.__awaiting_command_responses: dict[int, asyncio.Future[str]] = dict()

    def __get_correlation_id(self) -> int:
        self.__command_correlation_id += 1
        return self.__command_correlation_id

    async def __on_command_response(self, message: str) -> None:
        self._logger.debug("Received command response [%s]", message)

        message_dict = json.loads(message)

        if "correlation_id" not in message_dict:
            self._logger.error("correlation_id not in message")
            return

        if "payload" not in message_dict:
            self._logger.error("payload not in message")
            return

        if message_dict["correlation_id"] not in self.__awaiting_command_responses:
            self._logger.error("correlation_id not in awaiting command responses")
            return

        self.__awaiting_command_responses[message_dict["correlation_id"]].set_result(
            message_dict["payload"]
        )

    def subscribe_to_state(
        self, name: str, callback: Callable[[str], Coroutine[None, None, None]]
    ) -> None:
        self._logger.debug("Subscribing to state [%s]", name)
        self._adapter.subscribe(f"state/{name}", callback)

    def subscribe_to_event(
        self, name: str, callback: Callable[[str], Coroutine[None, None, None]]
    ) -> None:
        self._logger.debug("Subscribing to event [%s]", name)
        self._adapter.subscribe(f"event/{name}", callback)

    async def send_command(
        self,
        name: str,
        payload: str,
        timeout: int = 30,
    ) -> str:
        correlation_id = self.__get_correlation_id()
        request = json.dumps({"correlation_id": correlation_id, "payload": payload})

        self._logger.debug(
            "Sending command [%s] with payload [%s] and correlation_id [%d]",
            name,
            payload,
            correlation_id,
        )
        if not await self._adapter.publish(f"command/{name}", request):
            pass

        response_future = asyncio.Future()
        self.__awaiting_command_responses[correlation_id] = response_future

        try:
            response = await asyncio.wait_for(response_future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            del self.__awaiting_command_responses[correlation_id]
            raise RuntimeError("Command timed out")

    def run(self) -> None:
        self._logger.info("Running connector client")

        try:
            asyncio.run(self._adapter.connect())
        except KeyboardInterrupt:
            print("Keyboard interrupt")
