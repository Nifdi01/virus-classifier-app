from ml.src.universal_model import UniversalModel


class SklearnModel(UniversalModel):
    def __init__(self, name, sklearn_estimator):
        super().__init__(name)
        self.model = sklearn_estimator

    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)
        print(f"{self.name} training complete.")

    def predict(self, X):
        return self.model.predict(X)

    def predict_proba(self, X):
        return self.model.predict_proba(X)
