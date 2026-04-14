import re
from typing import NamedTuple, Optional


class DetectionResult(NamedTuple):
    is_malicious: bool
    confidence: float
    attack_type: str
    rule_matched: Optional[str] = None

class RuleDetector:
    def __init__(self):

        self.rules = {
            'sqli': [
                r"(\b|')OR(\b|')", r"1=1", r"UNION\s+SELECT", r"DROP\s+TABLE",
                r"';.*--", r"admin'--"
            ],
            'xss': [r"<script", r"javascript:", r"onerror=", r"alert\("],
            'rce': [r"(\||&|;)", r"(cat|ls|wget|curl)"],
            'path_trav': [r"\.\.\/", r"\/etc\/passwd"]
        }

    def classify(self, input_data: str) -> DetectionResult:
        """
        Sync rule-based detection with regex + legacy heuristics.
        """
        input_lower = input_data.lower()
        
        for attack_type, patterns in self.rules.items():
            for pattern in patterns:
                if re.search(pattern, input_data, re.IGNORECASE):
                    return DetectionResult(True, 0.8 + len(patterns)/10, attack_type, pattern)

        return DetectionResult(False, 0.0, "none")

