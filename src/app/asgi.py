from litestar import Litestar, get


@get("/")
async def index() -> str:
    return "Hello, world!"


@get("/books/{book_id:int}")
async def get_book(book_id: int) -> dict[str, int]:
    return {"book_id": book_id}


def create_app() -> Litestar:
    return Litestar(
        route_handlers=[index, get_book]
    )


app = create_app()
