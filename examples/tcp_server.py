import asyncio

# Add path to synapse module
import sys

sys.path.append("../")

# Add path to synapse module
import sys

from synapse.adapters.tcp_adapter import TCPAdapter
from synapse.connector import PAYLOAD
from synapse.connector_server import ConnectorServer

sys.path.append("../")

adapter = TCPAdapter()
connector_server = ConnectorServer(adapter)

async def handle_command_response(message: PAYLOAD):
    await asyncio.sleep(1)
    return f"Hello {message}"

connector_server.register_command("hello", handle_command_response)


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
