from fastapi import APIRouter, HTTPException
from app.schemas import PredictRequest, PredictResponse
from app.registry import registry
from app.inference import run_inference


router = APIRouter(prefix="/predict", tags=["predcit"])

@router.post("", response_model=PredictResponse)
def predict(request: PredictRequest):
    try:
        model = registry.get(request.model_name)
        result = run_inference(model, request.sequence)
        return PredictResponse(**result, model_used=request.model_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
