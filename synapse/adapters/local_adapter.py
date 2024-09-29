"""
A local adapter that connects to and communicates with a local Connector.

This adapter is used for testing and development purposes.
"""

import asyncio
import json

from ..logger import Logger
from .adapter import Adapter

logger = Logger("LocalAdapter")


class LocalAdapter(Adapter):
    def __init__(self, logger: Logger = logger) -> None:
        super().__init__(logger)

    async def connect(self):
        await super().connect()

    async def create(self):
        await super().create()

    def __on_message(self, message: str) -> None:
        message_dict = json.loads(message)

        if "topic" not in message_dict:
            print("[topic] key not in message")
            return
        if "message" not in message_dict:
            print("[message] key not in message")
            return

        if message_dict["topic"] in self.__subscribtions:
            asyncio.create_task(
                self.__subscribtions[message_dict["topic"]](message_dict["message"])
            )
        else:
            print(f"Unknown topic {message_dict['topic']}")

    async def publish(self, topic: str, message: str) -> None:
        self.__on_message(json.dumps({"topic": topic, "message": message}))
