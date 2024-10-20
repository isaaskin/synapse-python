import json
from typing import Tuple

from ..connector import PAYLOAD
from .errors import DeserializationError, SerializationError

# TODO: Replace raising errors with returning error
def deserialize_payload(message: str) -> PAYLOAD:
    try:
        return json.loads(message)
    except json.decoder.JSONDecodeError as e:
        # If the JSON is invalid, raise an error
        raise DeserializationError("Invalid JSON string") from e


# TODO: Replace raising errors with returning error
def serialize_payload(payload: PAYLOAD) -> str:
    try:
        return json.dumps(payload)
    except TypeError as e:
        # If the message is not in the correct format, raise an error
        raise SerializationError("Invalid payload format") from e


# TODO: Replace raising errors with returning error
def deserialize_command(message: str) -> Tuple[PAYLOAD, int]:
    try:
        message_dict = json.loads(message)

        if "correlation_id" not in message_dict:
            raise DeserializationError("correlation_id not in message")

        if "payload" not in message_dict:
            raise DeserializationError("payload not in message")

        return message_dict["payload"], message_dict["correlation_id"]
    except json.decoder.JSONDecodeError as e:
        # If the JSON is invalid, raise an error
        raise DeserializationError("Invalid JSON") from e


# TODO: Replace raising errors with returning error
def serialize_command(payload: PAYLOAD, correlation_id: int) -> str:
    try:
        return json.dumps({"payload": payload, "correlation_id": correlation_id})
    except TypeError as e:
        # If the message is not in the correct format, raise an error
        raise SerializationError("Invalid message format") from e
