import asyncio

# Add path to synapse module
import sys

sys.path.append("../")

from synapse.adapters.tcp_adapter import TCPAdapter
from synapse.connector_client import ConnectorClient

adapter = TCPAdapter()
connector_client = ConnectorClient(adapter)


async def send_command():
    while True:
        await asyncio.sleep(1)
        asyncio.create_task(connector_client.send_command("hello", "Worldsss"))


async def close_connection():
    print("Closing connection in 3 seconds")
    await asyncio.sleep(3)
    print("Closing connection")
    await adapter.close()


async def main():
    await asyncio.gather(adapter.connect(), close_connection())


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Keyboard interrupt")
