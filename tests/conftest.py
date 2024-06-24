from collections.abc import AsyncIterator

import pytest

from litestar import Litestar
from litestar.testing import AsyncTestClient

from app.asgi import app


@pytest.fixture(scope="function")
async def test_client() -> AsyncIterator[AsyncTestClient[Litestar]]:
    async with AsyncTestClient(app=app) as client:
        yield client


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"
