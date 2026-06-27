import sys, joblib
import ml.src.sklearn_model as _sklearn_module

# Register under every name the pickles might have used
sys.modules['__mp_main__'] = _sklearn_module
sys.modules['__main__'].__dict__.update(vars(_sklearn_module))

model_paths = [
    "ml/models/baseline/logistic_regression.pkl",
    "ml/models/baseline/random_forest.pkl",
    "ml/models/baseline/xgb_classifier.pkl",
    "ml/models/baseline/vectorizer.pkl",
    "ml/models/baseline/label_encoder.pkl",
]

for path in model_paths:
    try:
        obj = joblib.load(path)
        joblib.dump(obj, path)
        print(f"✓ Re-saved: {path}")
    except Exception as e:
        print(f"✗ Failed: {path} — {e}")
