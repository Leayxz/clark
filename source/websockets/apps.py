from ..telemetry.tracing import setup_tracing
from ..telemetry.logging import setup_logging

class Telemetry:

    @staticmethod
    def initialize() -> None:
        setup_tracing()
        setup_logging()
