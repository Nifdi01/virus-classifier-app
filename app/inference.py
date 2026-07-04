import numpy as np
from app.registry import SklearnBundle


def run_inference(model, sequences: list[str]) -> list[dict]:
    if isinstance(model, SklearnBundle):
        kmers = model.vectorizer.transform(sequences).toarray() / len(sequences)
        lengths = np.array([len(s) for s in sequences]).reshape(-1, 1)
        kmers = kmers / lengths

        labels = model.label_encoder.inverse_transform(model.model.predict(kmers))
        probas = model.model.predict_proba(kmers)
        classes = model.label_encoder.classes_
    else:
        labels = model.predict(sequences)
        probas = model.predict_proba(sequences)
        classes = model.label_encoder.classes_

    results = list()

    for seq, label, proba in zip(sequences, labels, probas):
        results.append({
            "influenza_type":str(label),
            "confidence": round(float(np.max(proba)), 4),
            "scores": {cls: round(float(p), 4) for cls, p in zip(classes, proba)},
            "sequence_length": len(seq)
        })

    return results
