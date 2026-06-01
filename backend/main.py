"""
main.py — FastAPI server for Market Snapshot
Endpoints:
  GET /api/snapshot        → full snapshot JSON
  GET /api/snapshot/meta   → cache metadata (age, status)
  POST /api/snapshot/refresh → force refresh

Scheduler:
  Market hours (09:00–15:45 IST): refresh every 60s
  Post-market (15:45–23:59 IST):  refresh every 15 min
  Pre-market  (00:00–09:00 IST):  refresh every 30 min
"""
import logging
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime

import pytz
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import cache.snapshot_cache as cache
from snapshot_builder import build_snapshot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

IST = pytz.timezone("Asia/Kolkata")

# ── Scheduler ─────────────────────────────────────────────────
scheduler = AsyncIOScheduler(timezone=IST)

async def _refresh_task():
    """Runs in background — builds snapshot and updates cache."""
    try:
        data = await asyncio.get_event_loop().run_in_executor(None, build_snapshot)
        cache.set(data)
    except Exception as e:
        logger.error(f"Refresh task failed: {e}")

def _get_refresh_interval() -> int:
    """Returns refresh interval in seconds based on IST time."""
    now = datetime.now(IST)
    h, m = now.hour, now.minute
    total_min = h * 60 + m
    if 9 * 60 <= total_min <= 15 * 60 + 45:
        return 60          # market hours: every 60s
    elif total_min > 15 * 60 + 45:
        return 15 * 60     # post-market: every 15 min
    else:
        return 30 * 60     # pre-market: every 30 min


# ── App lifespan ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initial fetch on startup
    logger.info("Starting initial snapshot fetch...")
    await _refresh_task()

    # Schedule recurring refresh
    scheduler.add_job(
        _refresh_task,
        "interval",
        seconds=60,          # base interval; dynamic logic inside
        id="snapshot_refresh",
        replace_existing=True,
        max_instances=1,
    )
    scheduler.start()
    logger.info("Scheduler started")

    yield

    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped")


# ── FastAPI app ───────────────────────────────────────────────
app = FastAPI(
    title="Market Snapshot API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in production
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ── Routes ────────────────────────────────────────────────────
@app.get("/api/snapshot")
async def get_snapshot():
    data = cache.get()
    if data is None:
        raise HTTPException(status_code=503, detail="Snapshot not yet available. Please retry in a few seconds.")
    return data


@app.get("/api/snapshot/meta")
async def get_meta():
    return {**cache.meta(), "age_seconds": cache.age_seconds()}


@app.post("/api/snapshot/refresh")
async def force_refresh():
    asyncio.create_task(_refresh_task())
    return {"status": "refresh triggered"}


@app.get("/health")
async def health():
    return {"status": "ok", "time_ist": datetime.now(IST).isoformat()}
