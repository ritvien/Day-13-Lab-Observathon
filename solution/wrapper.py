"""YOUR mitigation + observability layer. The simulator calls mitigate() around the
opaque agent (a REAL LLM) for every request. This is the ONLY place observability can
live -- the agent is silent. Legal moves: retry / cache / route / guardrail / sanitize
/ fallback / session-reset / PROMPT ROUTING, plus your own logging/tracing/metrics.
Illegal: hardcoding answers, importing the agent internals, reading instructor files,
network exfiltration.

  call_next(question, config) -> result   # the only way to reach the black box
  context = {"session_id","turn_index","qid","cache": <shared dict>, "cache_lock": <Lock>}
  result  = {"answer","status","steps","trace","meta":{latency_ms,usage,...}}

PROMPT ROUTING: you can override the agent's system prompt PER REQUEST by setting it in
the config you pass to call_next, e.g.:
    conf = dict(config); conf["system_prompt"] = my_better_prompt
    result = call_next(question, conf)
(Or just edit solution/prompt.txt for a single static prompt used on every request.)
"""
from __future__ import annotations

from telemetry.logger import logger
from telemetry.cost import cost_from_usage
from telemetry.redact import redact

def mitigate(call_next, question, config, context):
    cache_dict = context.get("cache", {})
    cache_lock = context.get("cache_lock")
    
    # Check Cache
    if cache_lock:
        with cache_lock:
            if question in cache_dict:
                return cache_dict[question]
    else:
        if question in cache_dict:
            return cache_dict[question]

    try:
        # Pass through to the real agent
        result = call_next(question, config)
        
        # Extract telemetry data
        meta = result.get("meta", {})
        usage = meta.get("usage", {})
        latency = meta.get("latency_ms", 0)
        model = config.get("model", "gpt-5.4-nano")
        cost = cost_from_usage(model, usage)
        
        # Log the full request details
        logger.log_event("agent_call", {
            "question": question,
            "answer": result.get("answer"),
            "status": result.get("status"),
            "latency_ms": latency,
            "cost_usd": cost,
            "usage": usage,
            "steps": result.get("steps", []),
            "trace": result.get("trace", [])
        })
        
        # FINAL SANITIZATION: Redact PII from the answer before returning to the simulator
        if result.get("answer") and config.get("redact_pii", False):
            result["answer"] = redact(result["answer"])[0]
            
        # Save successful results to Cache
        if result.get("status") == "ok":
            if cache_lock:
                with cache_lock:
                    cache_dict[question] = result
            else:
                cache_dict[question] = result
                
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()

