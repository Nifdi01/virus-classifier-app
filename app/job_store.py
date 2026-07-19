"""
Persists batch job metadata so jobs can be listed later.

Celery's result backend (Redis, in this case) only supports point lookups
by task_id — there's no way to enumerate all task IDs from it. This module
keeps a small side-index in Redis: a hash per job for metadata, plus a
sorted set (scored by submission time) so jobs can be listed newest-first
without an unbounded SCAN.
"""

from __future__ import annotations

import os
import time
from typing import TypedDict

import redis

_JOB_KEY_PREFIX = "job:"
_JOB_INDEX_KEY = "jobs:index"
_JOB_TTL_SECONDS = 60 * 60 * 24 * 30  # 30 days; adjust or drop as needed

_redis_client: redis.Redis | None = None


def get_redis_client() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        _redis_client = redis.from_url(redis_url, decode_responses=True)
    return _redis_client


class JobMetadata(TypedDict):
    task_id: str
    submitted_at: str  # ISO 8601
    sequence_count: int
    file_size_bytes: int | None
    model_name: str


def create_job(
    task_id: str,
    sequence_count: int,
    model_name: str,
    file_size_bytes: int | None = None,
) -> JobMetadata:
    """Call this right after `predict_batch_task.delay(...)` returns."""
    client = get_redis_client()
    now = time.time()
    submitted_at_iso = _to_iso(now)

    job_key = _JOB_KEY_PREFIX + task_id
    mapping = {
        "task_id": task_id,
        "submitted_at": submitted_at_iso,
        "sequence_count": sequence_count,
        "model_name": model_name,
        # Redis hashes can't store None; use empty string as a sentinel
        "file_size_bytes": file_size_bytes if file_size_bytes is not None else "",
    }

    pipe = client.pipeline()
    pipe.hset(job_key, mapping=mapping)
    pipe.expire(job_key, _JOB_TTL_SECONDS)
    pipe.zadd(_JOB_INDEX_KEY, {task_id: now})
    pipe.execute()

    return {
        "task_id": task_id,
        "submitted_at": submitted_at_iso,
        "sequence_count": sequence_count,
        "file_size_bytes": file_size_bytes,
        "model_name": model_name,
    }


def get_job_metadata(task_id: str) -> JobMetadata | None:
    client = get_redis_client()
    data = client.hgetall(_JOB_KEY_PREFIX + task_id)
    if not data:
        return None
    return _deserialize(data)


def list_job_metadata(limit: int = 50, offset: int = 0) -> list[JobMetadata]:
    """Newest-first, paginated."""
    client = get_redis_client()
    # zrevrange returns highest score (most recent) first
    task_ids = client.zrevrange(_JOB_INDEX_KEY, offset, offset + limit - 1)
    if not task_ids:
        return []

    pipe = client.pipeline()
    for task_id in task_ids:
        pipe.hgetall(_JOB_KEY_PREFIX + task_id)
    results = pipe.execute()

    jobs = []
    for task_id, data in zip(task_ids, results):
        if not data:
            # Metadata expired but index entry remains; skip and self-heal
            client.zrem(_JOB_INDEX_KEY, task_id)
            continue
        jobs.append(_deserialize(data))
    return jobs


def count_jobs() -> int:
    client = get_redis_client()
    return client.zcard(_JOB_INDEX_KEY)


def _deserialize(data: dict) -> JobMetadata:
    return {
        "task_id": data["task_id"],
        "submitted_at": data["submitted_at"],
        "sequence_count": int(data["sequence_count"]),
        "file_size_bytes": int(data["file_size_bytes"])
        if data["file_size_bytes"]
        else None,
        "model_name": data["model_name"],
    }


def _to_iso(epoch_seconds: float) -> str:
    from datetime import datetime, timezone

    return datetime.fromtimestamp(epoch_seconds, tz=timezone.utc).isoformat()
