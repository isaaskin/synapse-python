import asyncio

from behave import then, when
from behave.api.async_step import async_run_until_complete


@when("the client subscribes to the event")
def step_impl(context):
    context.handled_event = None

    async def handle_event(payload: str):
        context.handled_event = payload

    context.client.subscribe_to_event("hello", handle_event)


@when("the server publishes the event")
@async_run_until_complete
async def step_impl(context):
    await asyncio.sleep(1)
    await context.server.publish_event("hello", "World")


@then("the client receives the event")
def step_impl(context):
    assert context.handled_event == "World"
