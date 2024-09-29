"""
Module containing functions for serializing and deserializing messages.

The functions in this module are used by adapters to serialize and deserialize
messages. They are used by the `publish` and `subscribe` methods of the adapter
to convert messages to and from JSON strings.

"""
import json


class DeserializationError(Exception):
    """Raised when a message cannot be deserialized."""

    def __init__(self, message: str):
        super().__init__(message)


class SerializationError(Exception):
    """Raised when a message cannot be serialized."""

    def __init__(self, message: str):
        super().__init__(message)


def deserialize(message: str) -> dict:
    """Deserialize a message from a JSON string to a dictionary.

    This function takes a JSON string, parses it, and returns a dictionary
    containing the deserialized message. If the message is not in the correct
    format, it raises a DeserializationError.

    :param message: The JSON string to deserialize
    :return: A dictionary containing the deserialized message
    :raises DeserializationError: If the message is not in the correct format
    """
    try:
        # Parse the JSON string
        message_dict = json.loads(message)

        # Check that the message has the required fields
        if "topic" not in message_dict:
            raise DeserializationError("topic not in message")

        if "message" not in message_dict:
            raise DeserializationError("message not in message")

        # Return the deserialized message
        return message_dict

    except json.decoder.JSONDecodeError as e:
        # If the JSON is invalid, raise an error
        raise DeserializationError("Invalid JSON") from e


def serialize(topic: str, message: str) -> str:
    """Serialize a message dictionary to a JSON string.

    This function takes a topic and a message, and returns a JSON string
    containing the serialized message. If the message is not in the correct
    format, it raises a SerializationError.

    :param topic: The topic of the message
    :param message: The message to serialize
    :return: The serialized message
    :raises SerializationError: If the message is not in the correct format
    """
    try:
        # Create the message dictionary
        message_dict = {"topic": topic, "message": message}

        # Serialize the message dictionary to a JSON string
        return json.dumps(message_dict)

    except TypeError as e:
        # If the message is not in the correct format, raise an error
        raise SerializationError("Invalid message format") from e
