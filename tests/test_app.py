import pytest
from litestar import Litestar
from litestar.status_codes import HTTP_200_OK
from litestar.testing import AsyncTestClient


async def test_book_id_with_fixture(test_client: AsyncTestClient[Litestar]) -> None:
    response = await test_client.get("/books/{1}")
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"book_id": 1}
