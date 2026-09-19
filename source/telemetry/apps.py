from django.apps import AppConfig
from .tracing import setup_tracing
from .logging import setup_logging
from .metrics import setup_metrics

class TelemetryConfig(AppConfig):

    name = "source.telemetry"

    def ready(self) -> None:
        setup_tracing()
        setup_logging()
        setup_metrics()
