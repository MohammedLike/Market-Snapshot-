"""
cache/snapshot_cache.py
In-memory cache for the snapshot payload.
Thread-safe. No Redis dependency — pure Python dict + lock.
"""
import threading
import time
import logging

logger = logging.getLogger(__name__)

_lock    = threading.Lock()
_cache   = {
    "data":       None,
    "updated_at": 0,
    "status":     "initialising",
}

def get() -> dict | None:
    with _lock:
        return _cache["data"]

def set(data: dict) -> None:
    with _lock:
        _cache["data"]       = data
        _cache["updated_at"] = time.time()
        _cache["status"]     = "ok"
    logger.info("Snapshot cache updated")

def meta() -> dict:
    with _lock:
        return {
            "updated_at": _cache["updated_at"],
            "status":     _cache["status"],
            "has_data":   _cache["data"] is not None,
        }

def age_seconds() -> float:
    with _lock:
        if _cache["updated_at"] == 0:
            return float("inf")
        return time.time() - _cache["updated_at"]
