import asyncio
import sys
from threading import Thread

from behave import given, then, when
from behave.api.async_step import async_run_until_complete

sys.path.append("../../")

from synapse.adapters.ws_adapter import WSAdapter
from synapse.connector_client import ConnectorClient
from synapse.connector_server import ConnectorServer


def start_loop(loop):
    """Starts an asyncio event loop."""
    asyncio.set_event_loop(loop)
    loop.run_forever()


@given("a running server and a client")
@async_run_until_complete
async def step_impl(context):
    context.adapter_server = WSAdapter(port=1234)
    context.adapter_client = WSAdapter(port=1234)

    context.server = ConnectorServer(context.adapter_server)
    context.client = ConnectorClient(context.adapter_client)

    # Create two separate event loops
    context.loop1 = asyncio.new_event_loop()
    context.loop2 = asyncio.new_event_loop()

    # Start each loop in a separate thread
    context.t1 = Thread(target=start_loop, args=(context.loop1,))
    context.t2 = Thread(target=start_loop, args=(context.loop2,))

    context.t1.start()
    context.t2.start()

    # Schedule tasks in their respective loops
    context.loop1.call_soon_threadsafe(asyncio.create_task, context.adapter_server.create())
    await asyncio.sleep(1)
    context.loop2.call_soon_threadsafe(asyncio.create_task, context.adapter_client.connect())
    await asyncio.sleep(1)


@when("the client subscribes to state")
def step_impl(context):
    context.handled_state = None

    async def handle_state(payload: str):
        context.handled_state = payload

    context.client.subscribe_to_state("hello", handle_state)


@when("the server publishes state")
@async_run_until_complete
async def step_impl(context):
    await asyncio.sleep(1)
    await context.server.publish_state("hello", "World")


@then("the client receives the state")
def step_impl(context):
    assert context.handled_state == "World"


@then("close the server and client")
@async_run_until_complete
async def step_impl(context):
    print("Stopping loops...")
    context.loop1.call_soon_threadsafe(context.loop1.stop)
    context.loop2.call_soon_threadsafe(context.loop2.stop)
    context.t1.join()
    context.t2.join()
    print("Loops stopped.")
