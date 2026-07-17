from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from celery.result import AsyncResult

from typing import Literal, cast

from app.job_store import count_jobs, create_job, list_job_metadata
from worker import celery_app
from app.tasks import predict_batch_task
from app.schemas import (
    BatchPredictRequest,
    BatchPredictResponse,
    BatchProgress,
    JobListResponse,
    JobSummary,
    PredictionResult,
    ModelName,
)

router = APIRouter(prefix="/batch", tags=["batch"])

_SITE_MAP = {
    "PENDING": "PENDING",
    "RECEIVED": "PENDING",
    "STARTED": "PROGRESS",
    "RETRY": "PROGRESS",
    "PROGRESS": "PROGRESS",
    "SUCCESS": "SUCCESS",
    "FAILURE": "FAILURE",
}


@router.post("/predict", response_model=BatchPredictResponse)
def submit_batch(request: BatchPredictRequest):
    task = predict_batch_task.delay(request.sequences, request.model_name)

    try:
        create_job(
            task_id=task.id,
            sequence_count=len(request.sequences),
            model_name=request.model_name,
        )
    except Exception as e:
        print(f"Warning: Failed to record job metadata for {task.id}: {e}")

    return BatchPredictResponse(task_id=UUID(task.id), status="PENDING")


@router.get("/predict/{task_id}", response_model=BatchPredictResponse)
def get_batch_status(task_id: UUID):
    result = AsyncResult(str(task_id), app=celery_app)
    status = _SITE_MAP.get(result.state, "PENDING")

    if status == "PROGRESS":
        meta = result.info if isinstance(result.info, dict) else {}
        return BatchPredictResponse(
            task_id=task_id,
            status="PROGRESS",
            progress=BatchProgress(
                current=meta.get("current", 0), total=meta.get("total", 0)
            ),
        )
    if status == "FAILURE":
        raise HTTPException(status_code=500, detail=str(result.result))

    if status == "SUCCESS":
        results = [PredictionResult(**r) for r in result.get()]
        return BatchPredictResponse(task_id=task_id, status="SUCCESS", results=results)

    return BatchPredictResponse(task_id=task_id, status="PENDING")


@router.get("", response_model=JobListResponse)
def list_batches(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)):
    metadata_list = list_job_metadata(limit=limit, offset=offset)

    jobs = list()
    for meta in metadata_list:
        result = AsyncResult(meta["task_id"], app=celery_app)
        status = _SITE_MAP.get(result.state, "PENDING")
        status = cast(Literal["PENDING", "PROGRESS", "SUCCESS", "FAILURE"], status)
        jobs.append(
            JobSummary(
                task_id=UUID(meta["task_id"]),
                submitted_at=meta["submitted_at"],
                sequence_count=meta["sequence_count"],
                file_size_bytes=meta["file_size_bytes"],
                model_name=ModelName(meta["model_name"]),
                status=status,
            )
        )
    return JobListResponse(jobs=jobs, total=count_jobs())
