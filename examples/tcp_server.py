import asyncio

from synapse.adapters.tcp_adapter import TCPAdapter
from synapse.connector_server import ConnectorServer

adapter = TCPAdapter()
connector_server = ConnectorServer(adapter)

async def handle_command_response(message: str):
    await asyncio.sleep(1)
    return f"Hello {message}"

connector_server.register_command("hello", handle_command_response)


async def main():
    await adapter.create()


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Keyboard interrupt")
