import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class ResponseMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def log_message(self, message: str):
        print(message)

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())

        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Process-Id"] = request_id

        await self.log_message(
            f"Request ID: {request_id}, Time to response: {process_time:.3f}s"
        )
        return response
