import pytest
import asyncio


async def _do_nothing_async_function():
    pass


@pytest.mark.asyncio
async def test_async_sleep(timeline):
    timeline.set_time_factor(100)
    task = asyncio.ensure_future(_do_nothing_async_function())
    assert not task.done()
    timeline.sleep(5)
    await timeline.async_sleep(5)
    assert task.done()
