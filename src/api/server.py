"""LLMOps collector API."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
import time

app = FastAPI(title="LLMOps Monitor", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Prometheus metrics
REQUEST_DURATION = Histogram("llm_request_duration_seconds", "LLM request latency",
    ["model", "provider", "endpoint"], buckets=[0.1, 0.3, 0.5, 1.0, 2.0, 5.0, 10.0])
TOKENS_TOTAL = Counter("llm_tokens_total", "Total tokens used", ["model", "token_type"])
COST_TOTAL = Counter("llm_cost_usd_total", "Estimated cost USD", ["model", "provider"])
ERRORS_TOTAL = Counter("llm_errors_total", "LLM errors", ["model", "error_type"])
DRIFT_SCORE = Gauge("llm_prompt_drift_score", "Prompt drift score", ["model"])


class LLMTrace(BaseModel):
    model: str
    provider: str
    prompt: str
    response: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float
    cost_usd: float
    error: Optional[str] = None
    tags: dict = {}


@app.post("/trace")
async def ingest_trace(trace: LLMTrace):
    REQUEST_DURATION.labels(model=trace.model, provider=trace.provider, endpoint="/trace").observe(trace.latency_ms / 1000)
    TOKENS_TOTAL.labels(model=trace.model, token_type="prompt").inc(trace.prompt_tokens)
    TOKENS_TOTAL.labels(model=trace.model, token_type="completion").inc(trace.completion_tokens)
    COST_TOTAL.labels(model=trace.model, provider=trace.provider).inc(trace.cost_usd)
    if trace.error:
        ERRORS_TOTAL.labels(model=trace.model, error_type=trace.error).inc()
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/health")
def health(): return {"status": "ok", "time": time.time()}
