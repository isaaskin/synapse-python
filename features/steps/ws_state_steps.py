import asyncio

from behave import then, when
from behave.api.async_step import async_run_until_complete


@when("the client subscribes to the state")
def step_impl(context):
    context.handled_state = None

    async def handle_state(payload: str):
        context.handled_state = payload

    context.client.subscribe_to_state("hello", handle_state)


@when("the server publishes the state")
@async_run_until_complete
async def step_impl(context):
    await asyncio.sleep(1)
    await context.server.publish_state("hello", "World")


@then("the client receives the state")
def step_impl(context):
    assert context.handled_state == "World"
