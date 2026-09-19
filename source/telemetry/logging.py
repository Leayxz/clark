import logging
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter


def setup_logging():
    exporter = OTLPLogExporter(endpoint="http://localhost:4317", insecure=True)
    provider = LoggerProvider()
    provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
    set_logger_provider(provider)
    handler = LoggingHandler(level=logging.INFO, logger_provider=provider)
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.INFO)

logger = logging.getLogger(__name__)
