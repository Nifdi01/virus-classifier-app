import sys
from typing import Any
from dataclasses import dataclass

import joblib
import torch
from threading import Lock

sys.path.append("ml/src")
from ml.src.hyenadna_model import HyenaDNAModel
from ml.src.utils import load_model
from ml.src.sklearn_model import SklearnModel
import ml.src.sklearn_model as _sklearn_module

sys.modules['__mp_main__'] = _sklearn_module



MODEL_CONFIGS = {
    "hyenadna": {
        "type": "hyenadna",
        "path": "ml/models/hyenadna",
        "num_labels": 17,
        "label_encoder": "ml/models/hyenadna/label_encoder.pkl"
    },
    "logistic_regression": {
        "type": "sklearn",
        "path": "ml/models/baseline/logistic_regression.pkl",
        "vectorizer": "ml/models/baseline/vectorizer.pkl",
        "label_encoder": "ml/models/baseline/label_encoder.pkl"
    },
    "random_forest": {
        "type": "sklearn",
        "path": "ml/models/baseline/random_forest.pkl",
        "vectorizer": "ml/models/baseline/vectorizer.pkl",
        "label_encoder": "ml/models/baseline/label_encoder.pkl"
    },
    "xgb": {
        "type": "sklearn",
        "path": "ml/models/baseline/xgb_classifier.pkl",
        "vectorizer": "ml/models/baseline/vectorizer.pkl",
        "label_encoder": "ml/models/baseline/label_encoder.pkl"
    },
}


@dataclass
class SklearnBundle:
    model: Any
    vectorizer: Any
    label_encoder: Any

class ModelRegistry:
    def __init__(self):
        self._model = None
        self._active_name = None
        self._lock = Lock()

    def get(self, name: str):
        if name not in MODEL_CONFIGS:
            raise ValueError(f"Unkown Model {name}")
        
        with self._lock:
            if self._active_name == name:
                return self._model
            self._unload()
            self._model = self._load(name)
            self._active_name = name
            return self._model

    def _unload(self):
        if self._model is None:
            return
        del self._model
        self._model = None
        self._active_name = None
        torch.cuda.empty_cache() # helpful if we are on GPU

    def _load(self, name: str):
        cfg = MODEL_CONFIGS[name]
        if cfg["type"] == "hyenadna":
            return load_model(cfg["path"], cfg["num_labels"])
        return self._load_sklearn(cfg) 


    def _load_sklearn(self, cfg):
        model = joblib.load(cfg["path"])
        vectorizer = joblib.load(cfg["vectorizer"])
        label_encoder = joblib.load(cfg["label_encoder"])
        return SklearnBundle(model, vectorizer, label_encoder)


registry = ModelRegistry()
