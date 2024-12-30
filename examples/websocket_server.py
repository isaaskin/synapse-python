import asyncio
import random

# Add path to synapse module
import sys

sys.path.append("../")

from synapse.adapters.ws_adapter import WSAdapter
from synapse.connector import PAYLOAD
from synapse.connector_server import ConnectorServer

adapter = WSAdapter()
connector_server = ConnectorServer(adapter)


async def handle_command_response(message: PAYLOAD):
    await asyncio.sleep(random.randint(1, 2))
    return f"Hello {message}"


connector_server.register_command("hello", handle_command_response)


async def send_state():
    while True:
        await asyncio.sleep(1)
        await connector_server.publish_state("temperature", "23.4")


async def close_connection():
    print("Closing connection in 3 seconds")
    await asyncio.sleep(3)
    print("Closing connection")
    await adapter.close()


async def main():
    await asyncio.gather(adapter.create(), close_connection())


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Keyboard interrupt")
