import asyncio

# Add path to synapse module
import sys

sys.path.append("../")

from synapse.adapters.ws_adapter import WSAdapter
from synapse.connector_client import ConnectorClient

adapter = WSAdapter()
connector_client = ConnectorClient(adapter)


async def send_command():
    while True:
        await asyncio.sleep(1)
        asyncio.create_task(connector_client.send_command("hello", "Worldsss"))
        await asyncio.sleep(10)


async def handle_state(state):
    print(state)


connector_client.subscribe_to_state("temperature", handle_state)


async def main():
    await asyncio.gather(send_command(), adapter.connect())


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Keyboard interrupt")
