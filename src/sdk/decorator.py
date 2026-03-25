"""Zero-config LLM monitoring decorator."""
import time, functools, httpx
from typing import Optional

COST_PER_1K = {
    "gpt-4o": {"prompt": 0.005, "completion": 0.015},
    "gpt-4o-mini": {"prompt": 0.00015, "completion": 0.0006},
    "claude-3-5-sonnet-20241022": {"prompt": 0.003, "completion": 0.015},
}

def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    rates = COST_PER_1K.get(model, {"prompt": 0.001, "completion": 0.002})
    return (prompt_tokens * rates["prompt"] + completion_tokens * rates["completion"]) / 1000

def monitor_llm(model: str, provider: str = "openai", collector_url: str = "http://localhost:8002", tags: dict = {}):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            error = None
            result = None
            prompt_tokens = completion_tokens = 0
            try:
                result = func(*args, **kwargs)
                if hasattr(result, "usage"):
                    prompt_tokens = result.usage.prompt_tokens
                    completion_tokens = result.usage.completion_tokens
            except Exception as e:
                error = type(e).__name__
                raise
            finally:
                latency_ms = (time.time() - start) * 1000
                cost = estimate_cost(model, prompt_tokens, completion_tokens)
                try:
                    httpx.post(f"{collector_url}/trace", json={
                        "model": model, "provider": provider,
                        "prompt": str(args[0]) if args else "",
                        "response": str(result) if result else "",
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "latency_ms": latency_ms,
                        "cost_usd": cost,
                        "error": error,
                        "tags": tags
                    }, timeout=1.0)
                except Exception:
                    pass
            return result
        return wrapper
    return decorator
