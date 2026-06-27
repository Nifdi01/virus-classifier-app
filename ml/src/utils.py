import pickle
import os
import torch

from ml.src.hyenadna_model import HyenaDNAModel
from transformers import AutoTokenizer

def save_model(model, path):
    os.makedirs(path, exist_ok=True)
    torch.save(model.model.state_dict(), os.path.join(path, "model.pt"))
    model.tokenizer.save_pretrained(path)
    with open(os.path.join(path, "label_encoder.pkl"), "wb") as f:
        pickle.dump(model.label_encoder, f)
    print(f"Saved to {path}")


def load_model(path, num_labels):
    m = HyenaDNAModel(num_labels=num_labels)
    m.model.load_state_dict(torch.load(os.path.join(path, "model.pt"), map_location=m.device))
    m.tokenizer = AutoTokenizer.from_pretrained(path, trust_remote_code=True)
    with open(os.path.join(path, "label_encoder.pkl"), "rb") as f:
        m.label_encoder = pickle.load(f)
    return m
