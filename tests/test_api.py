import importlib
import sys
import types
import unittest
from unittest.mock import patch

from fastapi import HTTPException
from pydantic import ValidationError

from app.schemas import ModelName, PredictRequest


def load_predict_module(registry_get, inference_result=None, inference_error=None):
    fake_registry_module = types.ModuleType("app.registry")
    setattr(
        fake_registry_module,
        "registry",
        types.SimpleNamespace(get=registry_get),
    )

    def fake_run_inference(model, sequences):
        if inference_error is not None:
            raise inference_error
        return inference_result

    fake_inference_module = types.ModuleType("app.inference")
    setattr(fake_inference_module, "run_inference", fake_run_inference)

    with patch.dict(
        sys.modules,
        {
            "app.registry": fake_registry_module,
            "app.inference": fake_inference_module,
        },
    ):
        sys.modules.pop("app.routes.predict", None)
        return importlib.import_module("app.routes.predict")


class PredictRequestTests(unittest.TestCase):
    def test_predict_request_normalizes_sequence(self):
        request = PredictRequest(sequence="  acgtN  ")
        self.assertEqual(request.sequence, "ACGTN")

    def test_predict_request_rejects_invalid_dna(self):
        with self.assertRaises(ValidationError):
            PredictRequest(sequence="ACGTX")


class PredictRouteTests(unittest.TestCase):
    def test_predict_success_returns_response(self):
        module = load_predict_module(
            registry_get=lambda _: object(),
            inference_result=[
                {
                    "influenza_type": "H1N1",
                    "confidence": 0.4929,
                    "scores": {
                        "H1N1": 0.4929,
                        "H1N2": 0.0053,
                        "H3N2": 0.0017,
                        "H3N8": 0.0025,
                        "H4N6": 0.0002,
                        "H5N1": 0.0468,
                        "H5N2": 0.0004,
                        "H5N6": 0.0001,
                        "H5N8": 0.0011,
                        "H6N2": 0.0036,
                        "H7N2": 0.0005,
                        "H7N3": 0.0002,
                        "H7N7": 0.0009,
                        "H7N9": 0.0013,
                        "H9N2": 0.0124,
                        "influenza B": 0.4226,
                        "influenza D": 0.0075,
                    },
                    "sequence_length": 12,
                }
            ],
        )

        response = module.predict(
            PredictRequest(sequence="AAATTTCCCGGG", model_name=ModelName.xgb)
        )
        self.assertEqual(response.model_used, ModelName.xgb)
        self.assertEqual(response.influenza_type, "H1N1")
        self.assertEqual(response.sequence_length, 12)

    def test_predict_converts_value_error_to_http_400(self):
        module = load_predict_module(
            registry_get=lambda _: object(),
            inference_error=ValueError("bad input"),
        )

        with self.assertRaises(HTTPException) as context:
            module.predict(PredictRequest(sequence="ACGTN", model_name=ModelName.xgb))

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "bad input")
