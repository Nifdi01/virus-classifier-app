from enum import Enum
from pydantic import BaseModel, field_validator

class ModelName(str, Enum):
    hyenadna = "hyenadna"
    logistic_regression = "logistic_regression"
    random_forest = "random_forest"
    xgb = "xgb"


class PredictRequest(BaseModel):
    sequence: str
    model_name: ModelName = ModelName.hyenadna

    @field_validator("sequence")
    @classmethod
    def validate_sequence(cls, v):
        v = v.strip().upper()
        invalid = set(v) - set("ATCGUN")
        if not v:
            raise ValueError("Sequence cannot be empty")
        if invalid:
            raise ValueError("Invalid neucliotide characters: {invalid}")

        return v


class PredictResponse(BaseModel):
    influenza_type: str
    confidence: float
    scores: dict[str, float]
    sequence_lengh: int
    model_used: str



