from collections.abc import AsyncIterator

import pytest

from litestar import Litestar
from litestar.testing import AsyncTestClient

from app import app

pytestmark = pytest.mark.anyio


@pytest.fixture(scope="function")
async def test_client() -> AsyncIterator[AsyncTestClient[Litestar]]:
    async with AsyncTestClient(app=app) as client:
        yield client
