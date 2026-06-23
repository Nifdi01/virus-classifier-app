from abc import ABC, abstractmethod
from joblib.numpy_pickle import pickle
from sklearn import metrics
import time
import numpy as np

class UniversalModel(ABC):
    def __init__(self, name):
        self.name = name
        self.model = None

    @abstractmethod
    def train(self, X_train, y_train):
        pass

    @abstractmethod
    def predict(self, X):
        pass

    def evaluate(self, X_test, y_test, target_names, label_encoder=None):
        start = time.perf_counter()
        predictions = self.predict(X_test)
        prediction_time_s = time.perf_counter() - start
        prediction_time_per_sample_ms = (prediction_time_s / len(X_test)) * 1000
    
        _le = getattr(self, "label_encoder", None) or label_encoder
    
        # Normalize: encode predictions to integers if they are strings
        if predictions.dtype.kind in ('U', 'O') and _le is not None:
            predictions_encoded = _le.transform(predictions)
        else:
            predictions_encoded = predictions
    
        # Normalize: encode y_test to integers if it is strings
        if np.asarray(y_test).dtype.kind in ('U', 'O') and _le is not None:
            y_test_encoded = _le.transform(y_test)
        else:
            y_test_encoded = np.asarray(y_test)
    
        y_scores = None
        for method in ("predict_proba", "decision_function"):
            fn = getattr(self, method, None)
            if fn:
                try:
                    y_scores = fn(X_test)
                    break
                except Exception:
                    pass
    
        report = metrics.classification_report(
            y_test_encoded, predictions_encoded, target_names=target_names
        )
        confusion_matrix = metrics.confusion_matrix(y_test_encoded, predictions_encoded)
        macro_f1 = metrics.f1_score(y_test_encoded, predictions_encoded, average="macro")
        weighted_f1 = metrics.f1_score(y_test_encoded, predictions_encoded, average="weighted")
    
        unique_labels = np.unique(y_test_encoded)
        per_class_f1 = metrics.f1_score(
            y_test_encoded, predictions_encoded, average=None, labels=unique_labels
        )
        accuracy = metrics.accuracy_score(y_test_encoded, predictions_encoded)
    
        roc_curves, auc_scores, pr_curves, avg_precisions = {}, {}, {}, {}
        macro_auc = None
    
        if y_scores is not None:
            for i, cls in enumerate(target_names):
                int_label = _le.transform([cls])[0] if _le is not None else i
                score_col = y_scores[:, int_label]
                y_bin = (y_test_encoded == int_label).astype(int)
    
                fpr, tpr, roc_thresh = metrics.roc_curve(y_bin, score_col)
                prec, rec, pr_thresh = metrics.precision_recall_curve(y_bin, score_col)
                roc_curves[cls] = (fpr, tpr, roc_thresh)
                auc_scores[cls] = metrics.roc_auc_score(y_bin, score_col)
                pr_curves[cls] = (prec, rec, pr_thresh)
                avg_precisions[cls] = metrics.average_precision_score(y_bin, score_col)
    
            macro_auc = metrics.roc_auc_score(
                y_test_encoded, y_scores, multi_class='ovr', average="macro"
            )
    
        try:
            model_size_bytes = len(pickle.dumps(self.model))
        except Exception:
            model_size_bytes = None
    
        eval_results = {
            "accuracy": accuracy,
            "macro_f1": macro_f1,
            "weighted_f1": weighted_f1,
            "per_class_f1": dict(zip(target_names, per_class_f1.tolist())),
            "report": report,
            "confusion_matrix": confusion_matrix,
            "roc_curves": roc_curves,
            "auc_scores": auc_scores,
            "macro_auc": macro_auc,
            "pr_curves": pr_curves,
            "avg_precisions": avg_precisions,
            "prediction_time_s": prediction_time_s,
            "prediction_time_per_sample_ms": prediction_time_per_sample_ms,
            "model_size_bytes": model_size_bytes,
            "model_size_mb": model_size_bytes / (1024 ** 2) if model_size_bytes else None,
        }
    
        return report, macro_f1, confusion_matrix, eval_results

