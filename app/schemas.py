from enum import Enum
import re
from typing import Annotated, Literal
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


VALID_DNA = re.compile(r'^[ACTGN]+$', re.IGNORECASE)
MAX_SEQUENCE_LENGTH = 32_000 # Max length for HyenaDNA

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
        v = v[0]
        v = v.strip().upper()
        if not v:
            raise ValueError("Sequence cannot be empty")
        if not VALID_DNA.match(v):
            raise ValueError("Invalid nucleotide character detected.")

        return v


class PredictResponse(BaseModel):
    influenza_type: str
    confidence: float = Field(ge=0.0, le=1.0)
    scores: dict[str, Annotated[float, Field(ge=0.0, le=1.0)]]
    sequence_length: int
    model_used: str


class BatchProgress(BaseModel):
    current: int
    total: int


class PredictionResult(PredictResponse):
    sequence_index: int



class BatchPredictRequest(BaseModel):
    sequences: list[str]
    model_name: ModelName = ModelName.hyenadna

    @field_validator("sequences")
    @classmethod
    def validate_sequences(cls, v):
        if not v: 
            raise ValueError("Sequences list cannot be empty.")
        if len(v) > 100:
            raise ValueError("Max 100 sequences per batch.")
        for i, seq in enumerate(v):
            seq = seq.strip().upper()
            if not seq:
                raise ValueError(f"Sequence at index {i} is empty")
            if len(seq) > MAX_SEQUENCE_LENGTH:
                raise ValueError(f"Sequence at index {i} exceeds max length of {MAX_SEQUENCE_LENGTH}")
            if not VALID_DNA.match(seq):
                raise ValueError(f"Sequence at index {i} contains invalid characters: {seq!r}")
        return [seq.strip().upper() for seq in v]


class BatchPredictResponse(BaseModel):
    task_id: UUID
    status: Literal["PENDING", "PROGRESS", "SUCCESS", "FAILURE"]
    progress: BatchProgress | None = None
    results: list[PredictionResult] | None = None


