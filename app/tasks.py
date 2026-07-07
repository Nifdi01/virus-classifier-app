from celery.utils.log import get_task_logger

from worker import celery_app
from app.registry import registry
from app.inference import run_inference


logger = get_task_logger(__name__)

BATCH_CHUNK_SIZE = 16

@celery_app.task(name="tasks.predict_batch", bind=True)
def predict_batch_task(self, sequences: list[str], model_name:str) -> list[dict]:
    model = registry.get(model_name)
    total = len(sequences)
    results: list[dict] = list()

    for i in range(0, total, BATCH_CHUNK_SIZE):
        chunk = sequences[i: i + BATCH_CHUNK_SIZE]
        chunk_results = run_inference(model, chunk)

        for offset, r in enumerate(chunk_results):
            r["sequence_index"] = i + offset
            r["model_used"] = model_name
        results.extend(chunk_results)

        completed = min(i + BATCH_CHUNK_SIZE, total)
        self.update_state(state="PROGRESS", meta={"current": completed, "total": total})
    return results
