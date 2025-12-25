import time
import random
import json
import hashlib
from typing import Any, Dict, List, Optional, Tuple
from openai import OpenAI
from server.core.config import Settings, load_settings
from server.core.logger import get_logger

log = get_logger("optiresume.llm")
_client: Optional[OpenAI] = None
_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}

def _get_client(s: Settings) -> OpenAI:
    global _client
    if _client:
        return _client
    if not s.openai_api_key:
        raise RuntimeError("Missing OPENAI_API_KEY")
    _client = OpenAI(api_key=s.openai_api_key)
    return _client

def _backoff(attempt: int) -> float:
    return (0.6 * (2 ** attempt)) + random.uniform(0.0, 0.4)

def _cache_key(model: str,json_mode: bool,messages: List[Dict[str, Any]]) -> str:
    blob = json.dumps({"m": model,"j": json_mode,"msg": messages,},sort_keys=True,ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()

def chat_messages(messages: List[Dict[str, Any]],*,model: Optional[str] = None,temperature: Optional[float] = None,max_tokens: Optional[int] = None,timeout_s: Optional[int] = None,retries: Optional[int] = None,json_mode: bool = False,settings: Optional[Settings] = None,cache_key: Optional[str] = None,) -> Dict[str, Any]:
    s = settings or load_settings()
    client = _get_client(s)

    model = model or s.openai_model_default
    temperature = s.openai_temperature_default if temperature is None else temperature
    max_tokens = s.openai_max_tokens_default if max_tokens is None else max_tokens
    timeout_s = s.openai_timeout_s if timeout_s is None else timeout_s
    retries = s.openai_retries if retries is None else retries

    ck = cache_key or _cache_key(model,json_mode,messages)
    if s.llm_cache_enabled:
        hit = _cache.get(ck)
        if hit:
            ts,payload = hit
            if (time.time() - ts) <= s.llm_cache_ttl_s:
                out = dict(payload)
                out["cache_hit"] = True
                return out
            _cache.pop(ck,None)

    t0 = time.time()
    last_err: Optional[Exception] = None

    for attempt in range(retries + 1):
        try:
            kwargs: Dict[str, Any] = {"model": model,"messages": messages,"temperature": temperature,"max_tokens": max_tokens,"timeout": timeout_s,}
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}

            r = client.chat.completions.create(**kwargs)
            text = (r.choices[0].message.content or "").strip()

            latency_ms = int((time.time() - t0) * 1000)
            out: Dict[str, Any] = {"text": text,"model": model,"latency_ms": latency_ms,"attempt": attempt,"json_mode": json_mode,"cache_hit": False,}

            if json_mode:
                out["json"] = json.loads(text)

            log.info("llm_call_ok",extra={"model": model,"latency_ms": latency_ms,"attempt": attempt,"json_mode": json_mode,},)

            if s.llm_cache_enabled:
                _cache[ck] = (time.time(),out)

            return out

        except Exception as e:
            last_err = e
            latency_ms = int((time.time() - t0) * 1000)

            log.warning("llm_call_failed",extra={"model": model,"latency_ms": latency_ms,"attempt": attempt,"json_mode": json_mode,"error": str(e),},)

            if attempt >= retries:
                break

            time.sleep(_backoff(attempt))

    raise RuntimeError(f"LLM call failed after retries: {str(last_err)}")