import os
import jwt
from typing import Optional, Dict, Any

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (BatchSpanProcessor)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter as GrpcOTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter as HttpOTLPSpanExporter
from urllib.parse import urlparse, ParseResult

from logger import getJSONLogger
logger = getJSONLogger('init_tracing')


def init_tracer_provider():
    tracer_provider = TracerProvider()
    trace.set_tracer_provider(tracer_provider)
    options = get_exporter_options()
    Exporter = HttpOTLPSpanExporter
    if options["headers"]["x-otlp-protocol"] == "grpc":
        Exporter = GrpcOTLPSpanExporter
    tracer_provider.add_span_processor(BatchSpanProcessor(Exporter(**options)))


def extract_collector_options(sl_token):
    collector_protocol = get_env("OTEL_AGENT_COLLECTOR_PROTOCOL", default="http", key_desc="collector protocol")
    if collector_protocol != "http":
        logger.fatal("only http is supported")
        return None, None
    collector_url = get_env("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT", key_desc="collector url", allow_empty=True)
    collector_port = get_env("OTEL_AGENT_COLLECTOR_PORT", default="443", key_desc="collector port")
    if not collector_url:
        collector_url = extract_token_collector_url(sl_token, collector_port, collector_protocol)
    return collector_url, collector_protocol


def extract_sl_token():
    token = get_env("RM_DEV_SL_TOKEN", key_desc="sl token")
    return token


def get_exporter_options():
    sl_token = extract_sl_token()
    collector_url, protocol = extract_collector_options(sl_token)
    headers: Dict[str, str] = {
        "authorization": f"Bearer {sl_token}",
        "x-otlp-protocol": protocol

    }
    endpoint: Optional[str] = collector_url
    logger.info(f"OTEL endpoint: {endpoint}, protocol: {protocol}")
    return {"endpoint": endpoint, "headers": headers}


def get_env(env_key, key_desc="", default="", allow_empty=False):
    env_value = os.getenv(env_key, default=default)
    if not env_value and not allow_empty:
        logger.fatal(f"empty {key_desc}")
    return env_value


def extract_token_collector_url(sl_token, collector_port, collector_protocol):
    claims: Dict[str, Any] = jwt.decode(sl_token, key="", algorithms=["RS512"], options={"verify_signature": False}) or {}
    sl_server = claims.get("x-sl-server", None)
    url_suffix = "/v1/traces" if collector_protocol == "http" else ""
    if not sl_server:
        logger.fatal(f"empty sl server")
        return ""
    parse_result: ParseResult = urlparse(sl_server)
    return f"{parse_result.scheme}://ingest.{parse_result.hostname}:{collector_port}{url_suffix}"
