from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


class ServiceException(Exception):
    def __init__(self, code, message, status_code=status.HTTP_400_BAD_REQUEST, details=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


import traceback


def exception_handler(exc, context):
    if isinstance(exc, ServiceException):
        return Response(
            {
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
            status=exc.status_code,
        )

    response = drf_exception_handler(exc, context)
    if response is None:
        traceback.print_exc()
        return Response(
            {
                "error": {
                    "code": "SERVER_ERROR",
                    "message": "Internal server error",
                    "details": {},
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if isinstance(exc, ValidationError):
        code = "VALIDATION_ERROR"
        # Build a user-readable message from field errors
        if isinstance(response.data, dict):
            field_messages = []
            for field, errors in response.data.items():
                if isinstance(errors, list):
                    for err in errors:
                        if field == "non_field_errors":
                            field_messages.append(str(err))
                        else:
                            readable_field = field.replace("_", " ").capitalize()
                            field_messages.append(f"{readable_field}: {err}")
                elif isinstance(errors, str):
                    if field == "non_field_errors":
                        field_messages.append(errors)
                    else:
                        readable_field = field.replace("_", " ").capitalize()
                        field_messages.append(f"{readable_field}: {errors}")
            message = ". ".join(field_messages) if field_messages else "Please check your input and try again."
        else:
            message = "Please check your input and try again."
    elif isinstance(exc, APIException):
        code = str(getattr(exc, "default_code", "ERROR")).upper()
        message = str(getattr(exc, "detail", "Request failed"))
    else:
        code = "ERROR"
        message = "Request failed"

    details = response.data if isinstance(response.data, dict) else {}

    response.data = {
        "error": {
            "code": code,
            "message": message,
            "details": details,
        }
    }
    return response
