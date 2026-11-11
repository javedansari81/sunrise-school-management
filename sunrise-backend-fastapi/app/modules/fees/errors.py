"""Errors raised by the fee module's services. They are HTTPExceptions, so FastAPI returns them as they are."""
from fastapi import HTTPException, status


class FeeError(HTTPException):
    status_code_default = status.HTTP_400_BAD_REQUEST

    def __init__(self, detail: str):
        super().__init__(status_code=self.status_code_default, detail=detail)


class NotFound(FeeError):
    status_code_default = status.HTTP_404_NOT_FOUND


class Conflict(FeeError):
    status_code_default = status.HTTP_409_CONFLICT


class Invalid(FeeError):
    status_code_default = status.HTTP_422_UNPROCESSABLE_ENTITY
