import threading
from contextlib import contextmanager

from app.core.config import MAX_CONCURRENT_EXPORTS


_semaphore = threading.BoundedSemaphore(value=MAX_CONCURRENT_EXPORTS)


@contextmanager
def export_slot():
    acquired = _semaphore.acquire(blocking=False)
    if not acquired:
        raise RuntimeError("export_limit_reached")
    try:
        yield
    finally:
        _semaphore.release()
