from behave.api.async_step import async_run_until_complete
from common import start_server_and_client, stop_server_and_client


@async_run_until_complete
async def before_all(context):
    await start_server_and_client(context)

def after_all(context):
    stop_server_and_client(context)
