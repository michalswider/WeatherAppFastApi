import logging

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .exceptions import ApplicationException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_exception_handler(app):
    @app.exception_handler(ApplicationException)
    async def custom_exception_handler(
        request: Request, error: ApplicationException
    ) -> JSONResponse:
        logger.error(
            f"Error handler caught at {request.url} with method {request.method}. {error}"
        )
        content, status_code = error.to_response()
        return JSONResponse(content=content, status_code=status_code)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, error: HTTPException
    ) -> JSONResponse:
        client_host = request.client.host if request.client else "unknown"
        logger.error(
            f"HTTPException caught at {request.url} with method {request.method}, user IP: {client_host}. {error}"
        )
        content = {"detail": error.detail}
        return JSONResponse(content=content, status_code=error.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, error: RequestValidationError
    ) -> JSONResponse:
        logger.error(f"Error handler caught pydantic error: {error}")
        errors = [{"field": e["loc"][-1], "message": e["msg"]} for e in error.errors()]
        return JSONResponse(content={"detail": errors}, status_code=422)
