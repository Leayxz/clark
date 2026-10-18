import os, psutil

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.metrics import CallbackOptions, Observation
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource


def setup_metrics() -> None:
    resource = Resource.create({ "service.name": "clark", "service.instance.id": "clark-web", })
    exporter = OTLPMetricExporter( endpoint="http://localhost:4317", insecure=True, )

    reader = PeriodicExportingMetricReader(exporter)
    provider = MeterProvider( resource=resource, metric_readers=[reader], )

    metrics.set_meter_provider(provider)


def observe_memory(_: CallbackOptions):
    yield Observation(process.memory_info().rss)


process = psutil.Process(os.getpid())
meter = metrics.get_meter("clark")

page_views = meter.create_counter(name="http.page.views", description="Total number of HTTP page views.", unit="{view}")
meter.create_observable_gauge(name="process.memory.usage", callbacks=[observe_memory], description="Resident memory usage of the process.", unit="By")
