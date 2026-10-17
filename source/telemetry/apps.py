from django.apps import AppConfig

from .logging import setup_logging
from .metrics import setup_metrics
from .tracing import setup_tracing


class TelemetryConfig(AppConfig):

    name = "source.telemetry"

    def ready(self) -> None:
        setup_tracing()
        setup_logging()
        setup_metrics()
