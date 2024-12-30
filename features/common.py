import asyncio
import sys
from threading import Thread

sys.path.append("../")

from synapse.adapters.ws_adapter import WSAdapter
from synapse.connector_client import ConnectorClient
from synapse.connector_server import ConnectorServer


def start_loop(loop):
    """Starts an asyncio event loop."""
    asyncio.set_event_loop(loop)
    loop.run_forever()


async def start_server_and_client(context):
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


def stop_server_and_client(context):
    print("Stopping loops...")
    context.loop1.call_soon_threadsafe(context.loop1.stop)
    context.loop2.call_soon_threadsafe(context.loop2.stop)
    context.t1.join()
    context.t2.join()
    print("Loops stopped.")
