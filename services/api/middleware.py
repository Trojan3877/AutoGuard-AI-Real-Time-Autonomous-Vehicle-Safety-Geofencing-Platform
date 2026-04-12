"""FastAPI middleware: structured JSON logging and global error handling."""

import json
import logging
import time
import traceback
import uuid

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("autoguard.api")


def configure_logging(level: str = "INFO") -> None:
    """Configure root logger to emit structured JSON lines."""
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(message)s",
    )

    class _JsonFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:  # noqa: A003
            payload = {
                "ts": self.formatTime(record, self.datefmt),
                "level": record.levelname,
                "logger": record.name,
                "msg": record.getMessage(),
            }
            if record.exc_info:
                payload["exc"] = self.formatException(record.exc_info)
            return json.dumps(payload)

    for handler in logging.root.handlers:
        handler.setFormatter(_JsonFormatter())


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every request/response with timing and a correlation ID."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        start = time.perf_counter()

        logger.info(
            json.dumps(
                {
                    "event": "request_started",
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                }
            )
        )

        response: Response = await call_next(request)

        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(
            json.dumps(
                {
                    "event": "request_finished",
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": elapsed_ms,
                }
            )
        )

        response.headers["X-Request-ID"] = request_id
        return response


class GlobalExceptionMiddleware(BaseHTTPMiddleware):
    """Catch unhandled exceptions and return a structured 500 response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            return await call_next(request)
        except Exception:
            logger.error(
                json.dumps(
                    {
                        "event": "unhandled_exception",
                        "path": request.url.path,
                        "traceback": traceback.format_exc(),
                    }
                )
            )
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"},
            )
