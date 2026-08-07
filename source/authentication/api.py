from typing import cast, Any

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import AuthSerializer
from ..dtos import AuthDTO
from ..errors import Error, ERROR_CODE_MAPPING
from ..container import authentication_service


@api_view(["POST"])
def cadastrar_usuario(request):

    serializer = AuthSerializer(data=request.data)
    if not serializer.is_valid(): return Response({"error": Error.INVALID_CREDENTIALS.value}, status.HTTP_400_BAD_REQUEST)

    validated_data = cast(dict[str, Any], serializer.validated_data)
    user = AuthDTO(**validated_data)

    result = authentication_service.register(email=user.email, password=user.password)
    if result.error: return Response({"error": result.error.value}, ERROR_CODE_MAPPING[result.error])

    return Response({"message": "Usuário cadastrado com sucesso."}, status.HTTP_201_CREATED)


@api_view(["POST"])
def autenticar_usuario(request):
    
    serializer = AuthSerializer(data=request.data)
    if not serializer.is_valid(): return Response({"error": Error.INVALID_CREDENTIALS.value}, status.HTTP_400_BAD_REQUEST)
    
    validated_data = cast(dict[str, Any], serializer.validated_data)
    user = AuthDTO(**validated_data)

    result = authentication_service.authenticate(email=user.email, password=user.password)
    if result.error: return Response({"error": result.error.value}, ERROR_CODE_MAPPING[result.error])
    
    if result.access_token and result.refresh_token:
        response =  Response({"message": "Usuário autenticado com sucesso."}, status=status.HTTP_200_OK)
        response.set_cookie("access_token", result.access_token, httponly=True, secure=False, samesite="Lax")
        response.set_cookie("refresh_token", result.refresh_token, httponly=True, secure=False, samesite="Lax")
        return response


@api_view(["POST"])
def logout(request):
    response = Response({"message": "Logout realizado com sucesso."}, status.HTTP_200_OK)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response
