import pytest

from synapse.serializers.adapter_message_serializer import (DeserializationError,
                                                          SerializationError,
                                                          deserialize,
                                                          serialize)


def test_serialize():
    topic = "test_topic"
    message = "test_message"
    expected = '{"topic": "test_topic", "message": "test_message"}'

    actual = serialize(topic, message)

    assert actual == expected


def test_serialize_invalid_message():
    class Member:
        def __init__(self):
            self.name = "test_name"

    topic = "test_topic"
    message = Member()

    with pytest.raises(SerializationError):
        serialize(topic, message)  # type: ignore


def test_deserialize():
    message = '{"topic": "test_topic", "message": "test_message"}'
    expected = {"topic": "test_topic", "message": "test_message"}

    actual = deserialize(message)

    assert actual == expected


def test_deserialize_invalid_json():
    message = "invalid_json"

    with pytest.raises(DeserializationError):
        deserialize(message)
