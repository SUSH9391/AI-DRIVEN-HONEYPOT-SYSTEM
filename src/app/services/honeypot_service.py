from typing import Dict, Any
from app.detectors.rule_detector import RuleDetector
from app.detectors.ml_detector import MLDetector
from app.generators.fake_data import FakeDataGenerator
from app.services.logging_service import LoggingService
from app.services.session_service import SessionService
import asyncio

class HoneypotService:
    def __init__(
        self,
        rule_detector: RuleDetector,
        ml_detector: MLDetector,
        fake_gen: FakeDataGenerator,
        logger: LoggingService,
        session_svc: SessionService
    ):
        self.rule_detector = rule_detector
        self.ml_detector = ml_detector
        self.fake_gen = fake_gen
        self.logger = logger
        self.session_svc = session_svc

    async def handle_request(self, data: Dict[str, Any], background_tasks) -> Dict[str, Any]:
        """
        Main honeypot handler: rule detect → ML async if high conf → fake resp immediate → log background.
        """
        # Sync rule detection
        rule_result = self.rule_detector.classify(data)
        
        # Immediate fake response (don't block attacker)
        fake_resp = self.fake_gen.generate(data)
        
        # Async ML if rule conf high
        if rule_result.confidence > 0.6:
            background_tasks.add_task(self.ml_detector.score_async, data)
        
        # Background log + session update
        background_tasks.add_task(
            self.logger.write_attack, data, rule_result, fake_resp
        )
        
        return fake_resp

