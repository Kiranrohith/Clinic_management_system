import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

from app.utils.response import error_response

logger = logging.getLogger("clinic.api")


class BusinessRuleException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_handler(_: Request, exc: RequestValidationError):
        errors = [
            {"field": ".".join(map(str, err["loc"][1:])), "message": err["msg"]}
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response("Validation Failed", errors),
        )

    @app.exception_handler(HTTPException)
    async def http_handler(_: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(str(exc.detail), []),
        )

    @app.exception_handler(BusinessRuleException)
    async def business_handler(_: Request, exc: BusinessRuleException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response(exc.message, []),
        )

    @app.exception_handler(OperationalError)
    async def database_handler(_: Request, exc: OperationalError):
        logger.exception("Database operation failed.", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=error_response("Database connection failed. Please ensure the database server is running.", []),
        )

    @app.exception_handler(Exception)
    async def unhandled_handler(_: Request, exc: Exception):
        logger.exception("Unhandled server error.", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response("Internal server error.", []),
        )
