import logging
from functools import wraps

from django.conf import settings
from django.shortcuts import redirect

from rest_framework.response import Response
from rest_framework import status

from ..container import authentication_service

logger = logging.getLogger(__name__)


def authenticated(view):

    @wraps(view)
    def wrapper(request, *args, **kwargs):

        access_token = request.COOKIES.get("access_token")
        refresh_token = request.COOKIES.get("refresh_token")

        result = authentication_service.authorize(access_token, refresh_token)
        
        if result.error:
            if request.path.startswith("/api/"):
                logger.warning("API 401: %s — %s", request.path, result.error.value)
                return Response({"error": result.error.value}, status=status.HTTP_401_UNAUTHORIZED)

            logger.warning("Redirect login: %s — %s", request.path, result.error.value)
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")

        request.subject = result.subject
        response = view(request, *args, **kwargs)

        if result.new_access_token and result.new_refresh_token:
            response.set_cookie(key="access_token", value=result.new_access_token, httponly=True, secure=True, samesite="Lax")
            response.set_cookie(key="refresh_token", value=result.new_refresh_token, httponly=True, secure=True, samesite="Lax")

        return response
    return wrapper
