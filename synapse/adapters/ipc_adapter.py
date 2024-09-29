import asyncio
import json
from typing import Optional

import zmq
import zmq.asyncio

from ..logger import Logger
from .adapter import Adapter

logger = Logger("IPCAdapter")


class IPCAdapter(Adapter):
    def __init__(self, id: str = "synapse.ipc") -> None:
        super().__init__()

        self.__id = id

        self.__context = zmq.asyncio.Context()
        self.__socket: Optional[zmq.asyncio.Socket] = None

        self.__clients = set()

    async def __keep_listening(self) -> None:
        while True:
            if self.__socket is None:
                logger.error("Socket is None")
                break

            client_id, message = await self.__socket.recv_multipart()
            self.__socket.send_multipart([client_id, b"asd"])
            message = message.decode("utf-8")

            try:
                message_dict = json.loads(message)
            except json.decoder.JSONDecodeError as e:
                logger.error("Invalid JSON: [%s]. Error: %s", message, e)
                continue

            if "topic" not in message_dict:
                logger.error("topic not in message")
                continue

            if "message" not in message_dict:
                logger.error("message not in message")
                continue

            await self._notify_subscriber(
                message_dict["topic"], message_dict["message"]
            )

    async def connect(self) -> None:
        await super().connect()

        self.__socket = self.__context.socket(zmq.DEALER)
        self.__socket.connect("ipc://" + self.__id)
        self.__socket.setsockopt_string(zmq.IDENTITY, "777")

        self._set_connected(False, True)

        # await self.__keep_listening()
        while True:
            print("Listening for messages")
            msg = await self.__socket.recv()
            print(msg)

    async def create(self) -> None:
        await super().create()

        self.__socket = self.__context.socket(zmq.ROUTER)
        self.__socket.bind("ipc://" + self.__id)

        self._set_connected(True, True)

        await self.__keep_listening()

    async def publish(self, topic: str, message: str) -> None:
        print("publish", topic, message)
        data = json.dumps({"topic": topic, "message": message})

        if self.__socket:
            await self.__socket.send(data.encode("utf-8"))
