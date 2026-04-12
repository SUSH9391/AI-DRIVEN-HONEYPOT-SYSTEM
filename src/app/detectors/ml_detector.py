from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from core.config import settings
from typing import Dict, Any
import torch

class MLDetector:
    def __init__(self):
        model_name = settings.HF_MODEL_NAME
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        self.pipeline = pipeline(
            "text-classification",
            model=self.model,
            tokenizer=self.tokenizer,
            device=self.device,
            return_all_scores=True
        )

    async def score_async(self, data: Dict[str, Any]) -> float:
        """
        Async ML scoring via HF transformers (ARQ/background).
        Returns confidence 0.0-1.0 for malicious.
        """
        text = data.get("query", "") or data.get("body", {}).get("username", "")
        if not text:
            return 0.0
        
        results = self.pipeline(text)
        malicious_score = max([score["score"] for score in results[0] if "malicious" in score["label"].lower() or "attack" in score["label"].lower()], default=0.0)
        return min(malicious_score, 1.0)

