# 📊 LLMOps Monitor

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Prometheus](https://img.shields.io/badge/Prometheus-2.x-E6522C?style=flat&logo=prometheus)](https://prometheus.io)
[![Grafana](https://img.shields.io/badge/Grafana-10.x-F46800?style=flat&logo=grafana)](https://grafana.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Production LLM observability platform** — track latency, cost, token usage, hallucination rates, and prompt drift across every model call in real time.

## ✨ Highlights

- ⚡ **Zero-config instrumentation** — wrap any LLM call with one decorator
- 📈 **Prometheus + Grafana** — pre-built dashboards for p50/p95/p99 latency, cost per query, error rates
- 🔍 **Prompt drift detection** — embedding-based cosine similarity alerts when prompts shift
- 💰 **Cost tracking** — token-level cost estimation for OpenAI, Anthropic, Bedrock
- 🚨 **Alerting** — Slack/PagerDuty webhooks on threshold violations
- 🗃️ **Trace storage** — PostgreSQL with full request/response logging for replay

## Dashboard Preview

```
┌─────────────────────────────────────────────────────────┐
│  LLMOps Monitor Dashboard                               │
├──────────────┬──────────────┬───────────────┬──────────┤
│ Requests/min │ Avg Latency  │ Cost Today    │ Errors   │
│    1,247     │   843ms      │   $12.40      │  0.3%    │
├──────────────┴──────────────┴───────────────┴──────────┤
│  Latency Distribution (p50/p95/p99)                    │
│  ████████████░░░░░░░░░░░░░░░░░░░  p50: 620ms           │
│  ████████████████████░░░░░░░░░░░  p95: 1.8s            │
│  █████████████████████████░░░░░░  p99: 3.2s            │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
git clone https://github.com/rutvik29/llmops-monitor
cd llmops-monitor
docker-compose up -d  # starts Prometheus + Grafana

pip install -r requirements.txt
python -m src.api.server  # collector API at :8002

# Instrument your LLM calls
from src.sdk.decorator import monitor_llm

@monitor_llm(model="gpt-4o", tags={"env": "prod"})
def my_llm_call(prompt: str) -> str:
    return openai_client.chat.completions.create(...)
```

## Metrics Collected

| Metric | Type | Description |
|--------|------|-------------|
| `llm_request_duration_seconds` | Histogram | End-to-end latency |
| `llm_tokens_total` | Counter | Prompt + completion tokens |
| `llm_cost_usd_total` | Counter | Estimated cost in USD |
| `llm_errors_total` | Counter | Failures by error type |
| `llm_prompt_drift_score` | Gauge | Cosine similarity vs baseline |
| `llm_cache_hit_ratio` | Gauge | Semantic cache effectiveness |

## Architecture

```
LLM Calls → SDK Decorator → Collector API → Prometheus → Grafana
                                  ↓
                            PostgreSQL (full traces)
                                  ↓
                         Drift Detector → Slack Alerts
```

## License

MIT © Rutvik Trivedi
