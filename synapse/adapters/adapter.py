"""
Base class for message adapters.

This class is used as a common interface for message adapters.

"""

import asyncio
from typing import Callable, Coroutine

from ..logger import Logger

logger = Logger("Adapter")


class Adapter:
    def __init__(self, logger: Logger = logger) -> None:
        # Protected members
        """
        Initialize the adapter.

        :param logger: The logger to use for logging.
        """
        # Private members
        self.__subscribtions: dict[
            str, Callable[[str], Coroutine[None, None, None]]
        ] = dict()

        self.__is_server: bool = False
        self.__is_connected: bool = False

        # Protected methods
        self._logger = logger

    # protected methods
    def _update_connection_status(self, is_server: bool, is_connected: bool) -> None:
        """
        Update the connection status of the adapter.

        This method should be called by subclasses to notify the adapter
        that the connection status has changed.

        :param is_server: Whether the adapter is connected as a server or client.
        :param is_connected: Whether the adapter is connected.
        """

        self._logger.info(
            "Connected as %s",
            "server" if is_server else "client",
        )
        self.__is_server = is_server
        self.__is_connected = is_connected

    def _notify_subscriber(self, topic: str, message: str) -> None:
        """
        Notify all subscribers of a message.

        If the topic is not known, a warning is logged.

        :param topic: The topic of the message
        :param message: The message to notify
        """
        if topic in self.__subscribtions:
            asyncio.create_task(self.__subscribtions[topic](message))
            return

        self._logger.warning("Unknown topic [%s]", topic)

    def _log_already_connected(self) -> None:
        """
        Log a warning message if the adapter is already connected.

        This method should be called by subclasses to notify the adapter
        that it is already connected as a server or client.

        """
        self._logger.warning(
            "Already connected as a %s",
            "server" if self.__is_server else "client",
        )

    # public methods
    async def connect(self) -> bool:
        """
        Connect to a server or bind to a socket.

        Subclasses should override this method to implement the connection or
        binding logic.

        If the adapter is already connected, a warning is logged and False is returned.

        Returns:
            bool: True if the connection was successfully created, False otherwise
        """
        if self.is_connected():
            self._log_already_connected()
            return False
        return True

    async def create(self) -> bool:
        """
        Create a new connection.

        Subclasses should override this method to implement the creation logic.

        If the adapter is already connected as a server or client, a warning is logged
        and False is returned.

        :return: True if the connection was successfully created, False otherwise
        """
        if self.is_connected():
            self._log_already_connected()
            return False
        return True

    def subscribe(
        self, topic: str, callback: Callable[[str], Coroutine[None, None, None]]
    ) -> bool:
        """
        Subscribe to a topic.

        :param topic: The topic to subscribe to
        :param callback: The callback to call when a message is received
        :return: True if the subscription was successfully created, False otherwise
        """
        if topic in self.__subscribtions:
            logger.warning("Already subscribed to topic [%s]", topic)
            return False

        self.__subscribtions[topic] = callback

        return True

    async def publish(self, topic: str, message: str) -> bool:
        """
        Publish a message to a topic.

        :param topic: The topic to publish the message to
        :param message: The message to publish
        :return: True if the message was successfully published, False otherwise
        """
        
        if not self.is_connected():
            logger.error("Client is not connected")
            return False
        return True

    def is_connected(self) -> bool:
        """
        Check if the adapter is connected.

        :return: True if the adapter is connected, False otherwise
        """
        return self.__is_connected
