import unittest
from synapse.serializers.connector_messsage_serializer import (
    deserialize_payload,
    serialize_payload,
    deserialize_command,
    serialize_command,
)
from synapse.connector import PAYLOAD
from synapse.serializers.errors import DeserializationError, SerializationError


class InvalidPayload:
    pass


class TestConnectorMessageSerializer(unittest.TestCase):

    def test_deserialize_payload_valid_json(self):
        message = '{"key": "value"}'
        expected_payload = {"key": "value"}
        self.assertEqual(deserialize_payload(message), expected_payload)

    def test_deserialize_payload_invalid_json(self):
        message = "invalid_json"
        with self.assertRaises(DeserializationError):
            deserialize_payload(message)

    def test_serialize_payload_valid_payload(self):
        payload = {"key": "value"}
        expected_message = '{"key": "value"}'
        self.assertEqual(serialize_payload(payload), expected_message)

    def test_serialize_payload_invalid_payload(self):
        payload = InvalidPayload()
        with self.assertRaises(SerializationError):
            serialize_payload(payload) # type: ignore

    def test_deserialize_command_valid_command(self):
        message = '{"payload": {"key": "value"}, "correlation_id": 1}'
        expected_payload = {"key": "value"}
        expected_correlation_id = 1
        self.assertEqual(
            deserialize_command(message), (expected_payload, expected_correlation_id)
        )

    def test_deserialize_command_invalid_command(self):
        message = "invalid_command"
        with self.assertRaises(DeserializationError):
            deserialize_command(message)

    def test_deserialize_command_missing_correlation_id(self):
        message = '{"payload": {"key": "value"}}'
        with self.assertRaises(DeserializationError):
            deserialize_command(message)

    def test_deserialize_command_missing_payload(self):
        message = '{"correlation_id": 1}'
        with self.assertRaises(DeserializationError):
            deserialize_command(message)

    def test_serialize_command_valid_command(self):
        payload = {"key": "value"}
        correlation_id = 1
        expected_message = '{"payload": {"key": "value"}, "correlation_id": 1}'
        self.assertEqual(serialize_command(payload, correlation_id), expected_message)

    def test_serialize_command_invalid_command(self):
        class InvalidPayload:
            pass
        payload = InvalidPayload()
        correlation_id = 1
        with self.assertRaises(SerializationError):
            serialize_command(payload, correlation_id) # type: ignore


if __name__ == "__main__":
    unittest.main()
