class DeserializationError(Exception):
    """Raised when a message cannot be deserialized."""

    def __init__(self, message: str):
        super().__init__(message)


class SerializationError(Exception):
    """Raised when a message cannot be serialized."""

    def __init__(self, message: str):
        super().__init__(message)
