from abc import ABC, abstractmethod
from sklearn import metrics

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
        predictions = self.predict(X_test)
        
        report = metrics.classification_report(y_test, predictions, target_names=target_names, output_dict=True)
        macro_f1 = metrics.f1_score(y_test, predictions, average="macro")
        confusion_matrix = metrics.confusion_matrix(y_test, predictions)
        
        print(macro_f1)
        print(report)
        
        return report, macro_f1, confusion_matrix
