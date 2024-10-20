import asyncio
from typing import Callable, Coroutine, Optional, Tuple

from .adapters import Adapter
from .connector import PAYLOAD, Connector
from .logger import Logger
from .serializers import connector_messsage_serializer as cms


class ConnectorClient(Connector):
    def __init__(
        self, adapter: Adapter, logger: Logger = Logger("ConnectorClient")
    ) -> None:
        super().__init__(adapter, logger)

        self.__command_correlation_id = 0

        # Command responses
        self._adapter.subscribe("command/response", self.__on_command_response)
        self.__awaiting_command_responses: dict[int, asyncio.Future[PAYLOAD]] = dict()

    def __get_correlation_id(self) -> int:
        self.__command_correlation_id += 1
        return self.__command_correlation_id

    async def __on_command_response(self, message: str) -> None:
        self._logger.debug("Received command response [%s]", message)

        try:
            payload, correlation_id = cms.deserialize_command(message)
        except cms.DeserializationError as e:
            self._logger.error("Failed to deserialize command response: %s", e)
            return
        else:
            if correlation_id not in self.__awaiting_command_responses:
                self._logger.error("'correlation_id' not in awaiting command responses")
                return

            self.__awaiting_command_responses[correlation_id].set_result(payload)

    def subscribe_to_state(
        self, name: str, callback: Callable[[PAYLOAD], Coroutine[None, None, None]]
    ) -> None:
        self._logger.debug("Subscribing to state [%s]", name)

        async def _callback(message: str):
            try:
                payload = cms.deserialize_payload(message)
            except cms.DeserializationError as e:
                self._logger.error("Failed to deserialize state: %s", e)
                return
            else:
                await callback(payload)

        self._adapter.subscribe(f"state/{name}", _callback)

    def subscribe_to_event(
        self, name: str, callback: Callable[[PAYLOAD], Coroutine[None, None, None]]
    ) -> None:
        self._logger.debug("Subscribing to event [%s]", name)

        async def _callback(message: str):
            try:
                payload = cms.deserialize_payload(message)
            except cms.DeserializationError as e:
                self._logger.error("Failed to deserialize event: %s", e)
                return
            else:
                await callback(payload)

        self._adapter.subscribe(f"event/{name}", _callback)

    async def send_command(
        self,
        name: str,
        payload: str,
        timeout: int = 30,
    ) -> Tuple[Optional[PAYLOAD], bool]:
        correlation_id = self.__get_correlation_id()

        self._logger.debug(
            "Sending command [%s] with payload [%s] and correlation_id [%d]",
            name,
            payload,
            correlation_id,
        )

        try:
            request = cms.serialize_command(payload, correlation_id)
        except cms.SerializationError as e:
            self._logger.error("Failed to serialize command: %s", e)
            return None, False
        else:
            if not await self._adapter.publish(f"command/{name}", request):
                self._logger.error("Failed to send command [%s]", name)
                return None, False

            response_future: asyncio.Future[PAYLOAD] = asyncio.Future()
            self.__awaiting_command_responses[correlation_id] = response_future

            try:
                response = await asyncio.wait_for(response_future, timeout=timeout)
            except asyncio.TimeoutError:
                self._logger.error("Command [%s] timed out", name)
                return None, False
            finally:
                del self.__awaiting_command_responses[correlation_id]
                return response, True

    def run(self) -> None:
        self._logger.info("Running connector client")

        try:
            asyncio.run(self._adapter.connect())
        except KeyboardInterrupt:
            print("Keyboard interrupt")
