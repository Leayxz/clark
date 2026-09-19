import os, psutil

from opentelemetry import metrics
from opentelemetry.metrics import CallbackOptions, Observation
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader


def setup_metrics():
    exporter = OTLPMetricExporter(endpoint="http://localhost:4317", insecure=True)
    reader = PeriodicExportingMetricReader(exporter)
    provider = MeterProvider(metric_readers=[reader])
    metrics.set_meter_provider(provider)
    meter = metrics.get_meter("clark.dashboard")
    process = psutil.Process(os.getpid())

    def get_memory_usage(options: CallbackOptions):
        memory = process.memory_info().rss
        yield Observation(memory)

    meter.create_observable_gauge(name="process.memory.usage", callbacks=[get_memory_usage], description="Current resident memory usage of the Python process.", unit="By")
