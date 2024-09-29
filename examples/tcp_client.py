import asyncio

from synapse.adapters.tcp_adapter import TCPAdapter
from synapse.connector_client import ConnectorClient

adapter = TCPAdapter()
connector_client = ConnectorClient(adapter)


async def send_command():
    while True:
        await asyncio.sleep(1)
        asyncio.create_task(connector_client.send_command("hello", "Worldsss"))


async def main():
    await asyncio.gather(send_command(), adapter.connect())


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Keyboard interrupt")
