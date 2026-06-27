import numpy as np
from app.registry import SklearnBundle


def run_inference(model, sequence: str) -> dict:
    if isinstance(model, SklearnBundle):
        kmer = model.vectorizer.transform([sequence]).toarray() / len(sequence)
        label = model.label_encoder.inverse_transform(model.model.predict(kmer))[0]
        proba = model.model.predict_proba(kmer)[0]
        classes = model.label_encoder.classes_
    else:
        label = model.model.predict([sequence])[0]
        proba = model.model.predict_proba([sequence])[0]
        classes = model.label_encoder.classes_

    return {
        "influenza_type":str(label),
        "confidence": round(float(np.max(proba)), 4),
        "scores": {
            cls: round(float(p), 4) for cls, p in zip(classes, proba)
        },
        "sequence_length": len(sequence)
    }
