from django.http import JsonResponse

from .telemetry.logging import logger


class ExceptionHandlingMiddleware:
    """Middleware genérico que captura qualquer exceção não tratada."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        print(f"❌ Exceção não tratada: {exception}")
        logger.exception("❌ Exceção não tratada: %s", exception)
        return JsonResponse(data={}, status=500)
