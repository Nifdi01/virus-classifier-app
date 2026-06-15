from .universal_model import UniversalModel
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
from torch.utils.data import TensorDataset, DataLoader
from sklearn.preprocessing import LabelEncoder



class HyenaDNAModel(UniversalModel):
    def __init__(self, num_labels, model_name="LongSafari/hyenadna-small-32k-seqlen-hf"):
        super().__init__(name="HyenaDNA")
        self.num_labels = num_labels
        self.label_encoder = LabelEncoder()
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            num_labels=self.num_labels,
            trust_remote_code=True
        )
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    def _tokenize(self, X):
        return self.tokenizer(
            list(X),
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=32_000
        )

    def train(self, X_train, y_train, epochs=10, batch_size=16, lr=2e-5):
        encodings = self._tokenize(X_train)
        encoded_labels = self.label_encoder.transform(y_train)
        labels = torch.tensor(encoded_labels, dtype=torch.long)

        dataset = TensorDataset(encodings["input_ids"], labels)
        loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        optimizer = torch.optim.AdamW(self.model.parameters(), lr=lr)

        self.model.train()
        for epoch in range(epochs):
            total_loss = 0.0
            for input_ids, batch_labels in loader:
                input_ids = input_ids.to(self.device)
                batch_labels = input_ids.to(self.device)

                optimizer.zero_grad()
                outputs = self.model(input_ids=input_ids, labels=batch_labels)
                outputs.loss.backward()
                optimizer.step()
                
                total_loss += outputs.loss.item()

            print(f"Epoch {epoch + 1}/{epochs} — Loss: {total_loss / len(loader):.4f}")

    def predict(self, X):
        encodings = self._tokenize(X)
        dataset = TensorDataset(encodings["input_ids"])
        dataloader = DataLoader(dataset, batch_size=16)

        self.model.eval()
        all_preds = list()
        with torch.no_grad():
            for (input_ids, ) in dataloader:
                outputs = self.model(input_ids=input_ids.to(self.device))
                all_preds.extend(torch.argmax(outputs.logits, dim=1).cpu().numpy())
        return self.label_encoder.inverse_transform(all_preds)
                
