from rest_framework import status
from rest_framework.response import Response


def success_response(data=None, message="", status_code=status.HTTP_200_OK):
    return Response(
        {
            "success": True,
            "data": data or {},
            "message": message,
        },
        status=status_code,
    )
