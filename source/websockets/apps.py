from ..telemetry.logging import setup_logging
from ..telemetry.tracing import setup_tracing

class Telemetry:

    @staticmethod
    def initialize() -> None:
        setup_tracing()
        setup_logging()
