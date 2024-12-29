import asyncio

from ..logger import Logger
from ..serializers import adapter_message_serializer as ams
from .adapter import Adapter


class TCPAdapter(Adapter):
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8765,
        logger: Logger = Logger("TCPAdapter"),
    ) -> None:
        super().__init__(logger)

        self.__connection = None

        self.__host = host
        self.__port = port

        self.__writers: set[asyncio.StreamWriter] = set()

    # Private methods
    async def __on_connection(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        async def keep_listening(reader: asyncio.StreamReader) -> None:
            while True:
                data = await reader.read(1024)

                if len(data) == 0:
                    self._logger.info("Connection closed")
                    return

                message = data.decode("utf-8")

                try:
                    message_dict = ams.deserialize(message)
                except ams.DeserializationError as e:
                    self._logger.error(
                        "Error while deserializing message: %s, Error: %s", message, e
                    )
                    continue

                self._notify_subscriber(message_dict["topic"], message_dict["message"])

        self.__writers.add(writer)

        await keep_listening(reader)

        writer.close()
        await writer.wait_closed()

        self.__writers.remove(writer)

    # Public methods
    async def connect(self):
        if self.is_connected():
            self._log_already_connected()
            return

        try:
            reader, writer = await asyncio.open_connection(self.__host, self.__port)
            self.__connection = writer

            self._update_connection_status(False, True)

            self._logger.info("Connected to %s:%d", self.__host, self.__port)

            await self.__on_connection(reader, writer)
        except ConnectionRefusedError:
            self._logger.error("Connection refused to %s:%d", self.__host, self.__port)
            return

        # TODO handle other exceptions

    async def close(self) -> None:
        if not self.is_connected():
            self._logger.warning("Not connected")
            return

        if not self.is_connected():
            self._logger.warning("Not connected")
            return

        self.__connection.close()

        if self.is_server():
            self._update_connection_status(True, False)
        else:
            self._update_connection_status(False, False)

    async def create(self):
        if self.is_connected():
            self._log_already_connected()
            return

        self.__connection = await asyncio.start_server(
            self.__on_connection, self.__host, self.__port
        )

        self._update_connection_status(True, True)
        addrs = ", ".join(str(sock.getsockname()) for sock in self.__connection.sockets)
        self._logger.info("Listening on %s", addrs)

        async with self.__connection:
            try:
                await self.__connection.serve_forever()
            except asyncio.CancelledError:
                self._logger.info("Server stopped")

    async def publish(self, topic: str, message: str) -> bool:
        if not await super().publish(topic, message):
            return False

        try:
            serialized_message = ams.serialize(topic, message)
        except ams.SerializationError as e:
            self._logger.error(
                "Error while serializing message: %s, topic: %s, Error: %s",
                message,
                topic,
                e,
            )
            return False

        for writer in self.__writers:
            try:
                writer.write(serialized_message.encode("utf-8"))
                await writer.drain()
            except Exception as e:
                self._logger.error(
                    "Error while publishing message: %s, topic: %s, Error: %s",
                    message,
                    topic,
                    e,
                )

        return True
