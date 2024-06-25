from litestar import Litestar, get, Request


@get("/")
async def index() -> str:
    return "Hello, world!"


@get("/books/{book_id:int}")
async def get_book(book_id: int) -> dict[str, int]:
    return {"book_id": book_id}


@get("/request")
def my_router_handler(request: Request) -> None:
    request.logger.info("inside a request")
    return None


def create_app() -> Litestar:
    from app.config import app as config
    from app.config.base import get_settings

    settings = get_settings()

    return Litestar(
        cors_config=config.cors,
        debug=settings.app.DEBUG,
        route_handlers=[index, get_book, my_router_handler],

    )


app = create_app()
