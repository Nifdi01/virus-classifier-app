from uuid import UUID

from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult

from worker import celery_app
from app.tasks import predict_batch_task
from app.schemas import (
    BatchPredictRequest,
    BatchPredictResponse,
    BatchProgress,
    PredictionResult,
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
    return BatchPredictResponse(task_id=UUID(task.id), status="PENDING")


@router.get("/predict/{task_id}", response_model=BatchPredictResponse)
def get_batch_status(task_id: UUID):
    result = AsyncResult(str(task_id), app=celery_app)
    status = _SITE_MAP.get(result.state, "PENDING")

    print("status:", result.state)
    print("ready:", result.ready())
    print("info:", result.info)
    print("backend:", result.backend)

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
