from __future__ import annotations

import logging

import binascii
import json
import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

from litestar.utils.module_loader import module_to_os_path

if TYPE_CHECKING:
    from litestar.data_extractors import RequestExtractorField, ResponseExtractorField

DEFAULT_MODULE_NAME = "app"
BASE_DIR: Final[Path] = module_to_os_path(DEFAULT_MODULE_NAME)

TRUE_VALUES = {"True", "true", "1", "yes", "Y", "T"}


@dataclass
class ServerSettings:
    """Server configurations."""

    APP_LOC: str = "app.asgi:app"
    """Path to app executable, or factory."""
    APP_LOC_IS_FACTORY: bool = False
    """Indicate if APP_LOC points to an executable or factory."""
    HOST: str = field(default_factory=lambda: os.getenv("LITESTAR_HOST", "0.0.0.0"))  # noqa: S104
    """Server network host."""
    PORT: int = field(default_factory=lambda: int(os.getenv("LITESTAR_PORT", "8000")))
    """Server port."""
    KEEPALIVE: int = field(default_factory=lambda: int(os.getenv("LITESTAR_KEEPALIVE", "65")))
    """Seconds to hold connections open (65 is > AWS lb idle timeout)."""
    RELOAD: bool = field(
        default_factory=lambda: os.getenv("LITESTAR_RELOAD", "False") in TRUE_VALUES,
    )
    """Turn on hot reloading."""
    RELOAD_DIRS: list[str] = field(default_factory=lambda: [f"{BASE_DIR}"])
    """Directories to watch for reloading."""
    HTTP_WORKERS: int | None = field(
        default_factory=lambda: int(os.getenv("WEB_CONCURRENCY")) if os.getenv("WEB_CONCURRENCY") is not None else None,  # type: ignore[arg-type]
    )
    """Number of HTTP Worker processes to be spawned by Uvicorn."""


@dataclass
class LogSettings:
    """Logger configuration"""

    # https://stackoverflow.com/a/1845097/6560549
    EXCLUDE_PATHS: str = r"\A(?!x)x"
    """Regex to exclude paths from logging."""
    HTTP_EVENT: str = "HTTP"
    """Log event name for logs from Litestar handlers."""
    INCLUDE_COMPRESSED_BODY: bool = False
    """Include 'body' of compressed responses in log output."""
    LEVEL: int = field(default_factory=lambda: int(os.getenv("LOG_LEVEL", "10")))
    """Stdlib log levels.

    Only emit logs at this level, or higher.
    """
    OBFUSCATE_COOKIES: set[str] = field(default_factory=lambda: {"session"})
    """Request cookie keys to obfuscate."""
    OBFUSCATE_HEADERS: set[str] = field(default_factory=lambda: {"Authorization", "X-API-KEY"})
    """Request header keys to obfuscate."""
    JOB_FIELDS: list[str] = field(
        default_factory=lambda: [
            "function",
            "kwargs",
            "key",
            "scheduled",
            "attempts",
            "completed",
            "queued",
            "started",
            "result",
            "error",
        ],
    )
    """Attributes of the SAQ.

    [`Job`](https://github.com/tobymao/saq/blob/master/saq/job.py) to be
    logged.
    """
    REQUEST_FIELDS: list[RequestExtractorField] = field(
        default_factory=lambda: [
            "path",
            "method",
            "headers",
            "cookies",
            "query",
            "path_params",
            "body",
        ],
    )
    """Attributes of the [Request][litestar.connection.request.Request] to be
    logged."""
    RESPONSE_FIELDS: list[ResponseExtractorField] = field(
        default_factory=lambda: [
            "status_code",
            "cookies",
            "headers",
            "body",
        ],
    )
    """Attributes of the [Response][litestar.response.Response] to be
    logged."""
    WORKER_EVENT: str = "Worker"
    """Log event name for logs from SAQ worker."""
    SAQ_LEVEL: int = 20
    """Level to log SAQ logs."""
    SQLALCHEMY_LEVEL: int = 20
    """Level to log SQLAlchemy logs."""
    UVICORN_ACCESS_LEVEL: int = 20
    """Level to log uvicorn access logs."""
    UVICORN_ERROR_LEVEL: int = 20
    """Level to log uvicorn error logs."""
    GRANIAN_ACCESS_LEVEL: int = 30
    """Level to log uvicorn access logs."""
    GRANIAN_ERROR_LEVEL: int = 20
    """Level to log uvicorn error logs."""


@dataclass
class AppSettings:
    """Application configuration"""

    URL: str = field(default_factory=lambda: os.getenv("APP_URL", "http://localhost:8000"))
    """The frontend base URL"""
    DEBUG: bool = field(default_factory=lambda: os.getenv("LITESTAR_DEBUG", "False") in TRUE_VALUES)
    """Run `Litestar` with `debug=True`."""
    SECRET_KEY: str = field(
        default_factory=lambda: os.getenv("SECRET_KEY", binascii.hexlify(os.urandom(32)).decode(encoding="utf-8")),
    )
    """Application secret key."""
    NAME: str = field(default_factory=lambda: "app")
    """Application name."""
    ALLOWED_CORS_ORIGINS: list[str] | str = field(default_factory=lambda: os.getenv("ALLOWED_CORS_ORIGINS", '["*"]'))
    """Allowed CORS Origins"""
    CSRF_COOKIE_NAME: str = field(default_factory=lambda: "csrftoken")
    """CSRF Cookie Name"""
    CSRF_COOKIE_SECURE: bool = field(default_factory=lambda: False)
    """CSRF Secure Cookie"""
    JWT_ENCRYPTION_ALGORITHM: str = field(default_factory=lambda: "HS256")
    """JWT Encryption Algorithm"""

    def __post_init__(self) -> None:
        # Check if the ALLOWED_CORS_ORIGINS is a string.
        if isinstance(self.ALLOWED_CORS_ORIGINS, str):
            # Check if the string starts with "[" and ends with "]", indicating a list.
            if self.ALLOWED_CORS_ORIGINS.startswith("[") and self.ALLOWED_CORS_ORIGINS.endswith("]"):
                try:
                    # Safely evaluate the string as a Python list.
                    self.ALLOWED_CORS_ORIGINS = json.loads(self.ALLOWED_CORS_ORIGINS)
                except (SyntaxError, ValueError):
                    # Handle potential errors if the string is not a valid Python literal.
                    msg = "ALLOWED_CORS_ORIGINS is not a valid list representation."
                    raise ValueError(msg) from None
            else:
                # Split the string by commas into a list if it is not meant to be a list representation.
                self.ALLOWED_CORS_ORIGINS = [host.strip() for host in self.ALLOWED_CORS_ORIGINS.split(",")]


@dataclass
class Settings:
    app: AppSettings = field(default_factory=AppSettings)
    server: ServerSettings = field(default_factory=ServerSettings)
    log: LogSettings = field(default_factory=LogSettings)

    @classmethod
    def from_env(cls, dotenv_filename: str = ".env") -> Settings:
        from litestar.cli._utils import console

        env_file = Path(f"{os.curdir}/{dotenv_filename}")
        if env_file.is_file():
            from dotenv import load_dotenv

            logging.debug(f"Loading dotenv file from {dotenv_filename}.")
            console.print(f"[yellow]Loading environment configuration from {dotenv_filename}[/]")

            load_dotenv(env_file)
        return Settings()


@lru_cache(maxsize=1, typed=True)
def get_settings() -> Settings:
    return Settings.from_env()
