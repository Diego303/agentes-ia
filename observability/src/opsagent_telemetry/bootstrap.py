"""Arranque de OpenTelemetry configurado solo con variables de entorno estándar.

- ``OTEL_EXPORTER_OTLP_ENDPOINT``: si existe, trazas y métricas salen por OTLP/HTTP
  (en Kubernetes apunta al OpenTelemetry Collector).
- ``OTEL_TRACES_EXPORTER=console``: imprime los spans (desarrollo local).
- ``OTEL_SERVICE_NAME``: sustituye el nombre de servicio por defecto.

Sin endpoint ni consola se registra igualmente un ``TracerProvider``: el contexto de
traza se propaga (``traceparent``) aunque este proceso no exporte nada.
"""

from __future__ import annotations

import os

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter, SimpleSpanProcessor

_configured = False


def setup_telemetry(service_name: str, *, instrument_httpx: bool = False) -> None:
    """Registra los providers globales una sola vez por proceso.

    ``instrument_httpx`` propaga el contexto en las llamadas salientes con ``httpx``
    (el cliente A2A). El SDK de Anthropic y el de MCP ya crean sus spans y propagan
    ``traceparent`` por su cuenta.
    """
    global _configured
    if _configured or os.getenv("OTEL_SDK_DISABLED", "").lower() == "true":
        return
    resource = Resource.create(
        {
            "service.name": os.getenv("OTEL_SERVICE_NAME", service_name),
            "service.namespace": "agentes-ia",
        }
    )
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    traces_exporter = os.getenv("OTEL_TRACES_EXPORTER", "otlp" if endpoint else "none")

    tracer_provider = TracerProvider(resource=resource)
    if traces_exporter == "otlp" and endpoint:
        tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    elif traces_exporter == "console":
        tracer_provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(tracer_provider)

    readers = [PeriodicExportingMetricReader(OTLPMetricExporter())] if endpoint else []
    metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=readers))

    if instrument_httpx:
        HTTPXClientInstrumentor().instrument()
    _configured = True


def instrument_asgi(app):
    """Envuelve una app ASGI: extrae ``traceparent`` entrante y crea el span de servidor."""
    return OpenTelemetryMiddleware(app)


def shutdown_telemetry() -> None:
    """Vacía los exportadores antes de salir (llamar en el cierre del proceso)."""
    provider = trace.get_tracer_provider()
    if isinstance(provider, TracerProvider):
        provider.shutdown()
    meter_provider = metrics.get_meter_provider()
    if isinstance(meter_provider, MeterProvider):
        meter_provider.shutdown()
