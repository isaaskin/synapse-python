import asyncio

from synapse.adapters import Adapter


def test_when_updating_connection_status_then_is_connected_is_updated():
    """Test that updating the connection status is correctly handled."""

    adapter = Adapter()

    adapter._update_connection_status(True, True)

    assert adapter.is_connected()


async def test_given_a_topic_is_subscribed_when_notifying_then_callback_is_called():
    """Test that subscribing to a topic calls the callback function."""

    adapter = Adapter()
    topic = "topic"
    message = "message"

    future = asyncio.Future()

    async def callback(msg):
        future.set_result(None)

    adapter.subscribe(topic, callback)

    adapter._notify_subscriber(topic, message)

    try:
        await asyncio.wait_for(future, 3)
    except asyncio.TimeoutError:
        assert (
            False
        ), f"callback for topic {topic} was not called with message {message}"

    assert True
