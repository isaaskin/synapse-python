import asyncio

import websockets
from websockets import ConnectionClosedOK, WebSocketCommonProtocol
from websockets.exceptions import ConnectionClosedError
from websockets.server import serve

from ..logger import Logger
from ..serializers import adapter_message_serializer as ams
from .adapter import Adapter
from .errors import ConnectionError


class WSAdapter(Adapter):
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8765,
        logger: Logger = Logger("WebSocketAdapter"),
    ) -> None:
        super().__init__(logger)

        self.__host = host
        self.__port = port

        self.__connections: set[WebSocketCommonProtocol] = set()

    # Private methods
    async def __on_connection(self, websocket: WebSocketCommonProtocol) -> None:
        self._logger.info(
            "New connection: %s %s", websocket.path, websocket.remote_address
        )

        self.__connections.add(websocket)

        async def keep_listening(websocket: WebSocketCommonProtocol):
            async def on_message(message):
                try:
                    message_dict = ams.deserialize(message)
                    self._notify_subscriber(
                        message_dict["topic"], message_dict["message"]
                    )
                except ams.DeserializationError as e:
                    self._logger.error(
                        "Error while deserializing message: %s, Error: %s", message, e
                    )

            async for message in websocket:
                await on_message(message)

        try:
            await keep_listening(websocket)
            await websocket.wait_closed()
        except ConnectionClosedError:
            self._logger.warning(
                "Connection closed ungracefully: %s", websocket.remote_address
            )
        finally:
            self._logger.info("Connection closed: %s", websocket.remote_address)
            self.__connections.remove(websocket)

    async def connect(self):
        if self.is_connected():
            self._log_already_connected()
            return

        try:
            async with websockets.connect(
                f"ws://{self.__host}:{self.__port}"
            ) as websocket:
                self._update_connection_status(False, True)
                await self.__on_connection(websocket)
        except ConnectionRefusedError:
            raise ConnectionError(
                "Connection refused to %s:%d" % (self.__host, self.__port)
            )

    async def create(self):
        if self.is_connected():
            self._log_already_connected()
            return

        async with serve(
            self.__on_connection,
            self.__host,
            self.__port,
            extra_headers={
                "Access-Control-Allow-Origin": "*",
            },
        ):
            self._update_connection_status(True, True)
            await asyncio.Future()

    async def publish(self, topic: str, message: str) -> bool:
        if not await super().publish(topic, message):
            return False

        if len(self.__connections) == 0:
            self._logger.warning("No connections found")
            return False

        for connection in self.__connections:
            try:
                # Serialize the message
                serialized_message = ams.serialize(topic, message)

                # Send the message to the client
                await connection.send(serialized_message)
            except ams.SerializationError as e:
                # Handle serialization errors
                self._logger.error(
                    "Error while serializing message: %s, topic: %s, Error: %s",
                    message,
                    topic,
                    e,
                )
            except ConnectionClosedOK:
                # Handle connection closed errors
                self._logger.warning(
                    "Connection closed ungracefully: %s", connection.remote_address
                )
            except Exception as e:
                # Handle unknown errors
                self._logger.error(
                    "Unknown error while publishing message: %s, topic: %s, Error: %s",
                    message,
                    topic,
                    e,
                )

        return True
