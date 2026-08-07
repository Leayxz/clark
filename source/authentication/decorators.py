from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from ..container import authentication_service


def authenticated(view):

    @wraps(view)
    def wrapper(request, *args, **kwargs):

        access_token = request.COOKIES.get("access_token")
        refresh_token = request.COOKIES.get("refresh_token")

        result = authentication_service.authorize(access_token, refresh_token)
        if result.error: return Response({"error": result.error.value}, status=status.HTTP_401_UNAUTHORIZED)

        request.subject = result.subject

        response = view(request, *args, **kwargs)

        if result.new_access_token and result.new_refresh_token:
            response.set_cookie(key="access_token", value=result.new_access_token, httponly=True, secure=True, samesite="Lax")
            response.set_cookie(key="refresh_token", value=result.new_refresh_token, httponly=True, secure=True, samesite="Lax")

        return response

    return wrapper
