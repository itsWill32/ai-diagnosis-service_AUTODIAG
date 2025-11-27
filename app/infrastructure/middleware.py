

import time
import logging
from typing import Callable
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)




def setup_error_handlers(app: FastAPI) -> None:

    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):

        error_names = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            409: "CONFLICT",
            422: "UNPROCESSABLE_ENTITY",
            500: "INTERNAL_SERVER_ERROR"
        }
        
        error_name = error_names.get(exc.status_code, "HTTP_ERROR")
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": error_name,
                "message": exc.detail,
                "statusCode": exc.status_code
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):

        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            errors.append({
                "field": field,
                "message": message
            })
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "VALIDATION_ERROR",
                "message": "Invalid request data",
                "statusCode": 422,
                "details": errors
            }
        )




async def request_logging_middleware(request: Request, call_next: Callable):

    start_time = time.time()
    
    method = request.method
    path = request.url.path
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        response = await call_next(request)
        
        process_time = (time.time() - start_time) * 1000 
        
        logger.info(
            f"{method} {path} - {response.status_code} - "
            f"{process_time:.2f}ms - IP: {client_ip}"
        )
        
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        
        return response
        
    except Exception as e:
        process_time = (time.time() - start_time) * 1000
        logger.error(
            f"{method} {path} - ERROR - {process_time:.2f}ms - "
            f"IP: {client_ip} - Exception: {str(e)}"
        )
        raise




def get_cors_config_from_env(allowed_origins_str: str) -> dict:

    origins = [origin.strip() for origin in allowed_origins_str.split(",")]
    
    return {
        "allow_origins": origins,
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
        "expose_headers": ["X-Process-Time"],
        "max_age": 3600
    }




class RateLimitMiddleware:

    
    def __init__(self, app: FastAPI):
        self.app = app
    
    async def __call__(self, request: Request, call_next: Callable):

        response = await call_next(request)
        return response




async def security_headers_middleware(request: Request, call_next: Callable):

    response = await call_next(request)
    
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    return response



__all__ = [
    "setup_error_handlers",
    "request_logging_middleware",
    "get_cors_config_from_env",
    "RateLimitMiddleware",
    "security_headers_middleware"
]