from transformers import pipeline
import logging

logger = logging.getLogger(__name__)

class MLDetector:
    MODEL_NAME = "martin-ha/toxic-comment-model"
    
    def __init__(self):
        logger.info(f"Loading ML model: {self.MODEL_NAME}")
        self.classifier = pipeline(
            "text-classification",
            model=self.MODEL_NAME,
            device=-1,          # force CPU, never GPU
            truncation=True,
            max_length=128,     # short inputs only, keeps it fast
        )
        logger.info("ML model loaded successfully")

    def score(self, payload: dict) -> float:
        """
        Takes attack payload dict, returns confidence float 0.0-1.0.
        Combines all form field values into one string for classification.
        """
        try:
            text = " ".join(str(v) for v in payload.values())[:512]
            if not text.strip():
                return 0.0
            result = self.classifier(text)[0]
            # model returns label TOXIC/NON_TOXIC with score
            if result['label'] == 'TOXIC':
                return round(result['score'], 4)
            else:
                return round(1 - result['score'], 4)
        except Exception as e:
            logger.error(f"ML scoring failed: {e}")
            return 0.0
