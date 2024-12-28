import asyncio
import json
from typing import Awaitable, Callable

from .adapters import Adapter
from .connector import PAYLOAD, Connector
from .logger import Logger
from .serializers import connector_messsage_serializer as cms


class ConnectorServer(Connector):
    def __init__(
        self, adapter: Adapter, logger: Logger = Logger("ConnectorServer")
    ) -> None:
        super().__init__(adapter, logger)

        self.__commands: dict[str, Callable[[str], Awaitable[str]]] = dict()

    async def publish_state(self, name: str, payload: PAYLOAD) -> None:
        self._logger.debug("Publishing state [%s] with payload [%s]", name, payload)

        try:
            serialized_payload = cms.serialize_payload(payload)
        except cms.SerializationError as e:
            self._logger.error("Failed to serialize state: %s", e)
        else:
            if not await self._adapter.publish(f"state/{name}", serialized_payload):
                self._logger.error("Failed to publish state [%s]", name)

    async def publish_event(self, name: str, payload: str) -> None:
        self._logger.debug("Publishing event [%s] with payload [%s]", name, payload)

        try:
            serialized_payload = cms.serialize_payload(payload)
        except cms.SerializationError as e:
            self._logger.error("Failed to serialize event: %s", e)
        else:
            if not await self._adapter.publish(f"event/{name}", serialized_payload):
                self._logger.error("Failed to publish event [%s]", name)

    def register_command(
        self, name: str, callback: Callable[[PAYLOAD], Awaitable[PAYLOAD]]
    ) -> None:
        self._logger.debug("Registering command [%s]", name)

        if name in self.__commands:
            self._logger.warning("Command [%s] already registered", name)
            return

        async def process_command(message: str):
            self._logger.debug(
                "Processing command [%s] with message [%s]", name, message
            )

            try:
                payload, correlation_id = cms.deserialize_command(message)
            except cms.DeserializationError as e:
                self._logger.error("Failed to deserialize command: %s", e)
            else:
                try:
                    response = cms.serialize_payload(await callback(payload))
                except cms.SerializationError as e:
                    self._logger.error("Failed to serialize response: %s", e)
                else:
                    response_to_be_sent = json.dumps(
                        {"correlation_id": correlation_id, "payload": response}
                    )
                    if not await self._adapter.publish(
                        "command/response", response_to_be_sent
                    ):
                        self._logger.error("Failed to send command response")

        self._adapter.subscribe(f"command/{name}", process_command)

    def run(self) -> None:
        self._logger.info("Running connector server")

        try:
            asyncio.run(self._adapter.create())
        except KeyboardInterrupt:
            print("Keyboard interrupt")
