"""This module contains the OpenTelemetry telemetry setup for logging, tracing, and metrics."""
import logging
from azure.monitor.opentelemetry.exporter import (
    AzureMonitorLogExporter,
    AzureMonitorMetricExporter,
    AzureMonitorTraceExporter,
)
from opentelemetry._logs import set_logger_provider
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.metrics.view import DropAggregation, View
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.trace import set_tracer_provider


def _get_resource() -> Resource:
    """
    Get the resource to use for logging, tracing, and metrics.
    
    Returns:
        Resource: The resource to use.
    """
    return Resource.create({ResourceAttributes.SERVICE_NAME: "contoso.mysql_copilot"})


def set_up_logging(connection_string: str, resource: Resource = _get_resource()):
    """
    Set up logging with Azure Monitor.
    
    Args:
        connection_string (str): The Azure Monitor connection string.
        resource (Resource): The resource to use for logging.
    """
    exporter = AzureMonitorLogExporter(connection_string=connection_string)
    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
    set_logger_provider(logger_provider)
    handler = LoggingHandler()
    handler.addFilter(logging.Filter("semantic_kernel"))
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def set_up_tracing(connection_string: str, resource: Resource = _get_resource()):
    """
    Set up tracing with Azure Monitor.
    
    Args:
        connection_string (str): The Azure Monitor connection string.
        resource (Resource): The resource to use for tracing.
    """
    exporter = AzureMonitorTraceExporter(connection_string=connection_string)
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
    set_tracer_provider(tracer_provider)


def set_up_metrics(connection_string: str, resource: Resource = _get_resource()):
    """
    Set up metrics with Azure Monitor.
    
    Args:
        connection_string (str): The Azure Monitor connection string.
        resource (Resource): The resource to use for metrics.
    """
    exporter = AzureMonitorMetricExporter(connection_string=connection_string)
    meter_provider = MeterProvider(
        metric_readers=[
            PeriodicExportingMetricReader(exporter, export_interval_millis=5000)
        ],
        resource=resource,
        views=[
            View(instrument_name="*", aggregation=DropAggregation()),
            View(instrument_name="semantic_kernel*"),
        ],
    )
    set_meter_provider(meter_provider)
