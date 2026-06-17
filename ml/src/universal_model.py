from abc import ABC, abstractmethod
from joblib.numpy_pickle import pickle
from sklearn import metrics
import time

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

    def evaluate(self, X_test, y_test, target_names):
        start = time.perf_counter()
        predictions = self.predict(X_test)
        prediction_time_s = time.perf_counter() - start
        prediction_time_per_sample_ms = (prediction_time_s / len(X_test)) * 1000

        y_scores = None

        for method in ("predict_proba", "decision_function"):
            fn = getattr(self, method, None)
            if fn:
                try:
                    y_scores = fn(X_test)
                    break
                except Exception:
                    pass

        report = metrics.classification_report(y_test, predictions, target_names=target_names)
        confusion_matrix = metrics.confusion_matrix(y_test, predictions)
        macro_f1 = metrics.f1_score(y_test, predictions, average="macro")
        weighted_f1 = metrics.f1_score(y_test, predictions, average="weighted")
        per_class_f1 = metrics.f1_score(y_test, predictions, average=None, labels=target_names)
        accuracy = metrics.accuracy_score(y_test, predictions)

        roc_curves, auc_scores, pr_curves, avg_precisions = {}, {}, {}, {}
        macro_auc = None

        if y_scores is not None:
            for i, cls in enumerate(target_names):
                score_col = y_scores[:, i]
                y_bin = (y_test == cls).astype(int)
                
                fpr, tpr, roc_thresh = metrics.roc_curve(y_bin, score_col)
                prec, rec, pr_thresh = metrics.precision_recall_curve(y_bin, score_col)
                roc_curves[cls] = (fpr, tpr, roc_thresh)
                auc_scores[cls] = metrics.roc_auc_score(y_bin, score_col)
                pr_curves[cls] = (prec, rec, pr_thresh)
                avg_precisions[cls] = metrics.average_precision_score(y_bin, score_col)

            macro_auc = metrics.roc_auc_score(
                y_test, y_scores, multi_class='ovr', average="macro"
            )

        try:
            model_size_bytes = len(pickle.dumps(self.model))
        except Exception:
            model_size_bytes = None

        eval_results = {
            "accuracy": accuracy,
            "macro_f1": macro_f1,
            "weighted_f1": weighted_f1,
            "per_class_f1": dict(zip(target_names,per_class_f1.tolist())),
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

