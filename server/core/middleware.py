import time
import uuid
from fastapi import Request
from server.core.logger import get_logger, set_request_id

log = get_logger("optiresume.middleware")

async def request_context_middleware(request: Request,call_next):
    request_id = str(uuid.uuid4())
    set_request_id(request_id)

    start = time.time()

    try:
        response = await call_next(request)
        return response

    except Exception:
        latency_ms = int((time.time() - start) * 1000)
        log.exception("unhandled_request_error",extra={"path": str(request.url.path),"method": request.method,"latency_ms": latency_ms,},)
        raise

    finally:
        latency_ms = int((time.time() - start) * 1000)
        log.info("request_completed",extra={"path": str(request.url.path),"method": request.method,"latency_ms": latency_ms,"status": getattr(getattr(request,"state",None),"status",None),},)