from typing import Dict, Any
from app.detectors.rule_detector import RuleDetector
from app.detectors.ml_detector import MLDetector
from app.generators.fake_data import FakeDataGenerator
from app.services.logging_service import LoggingService
from app.services.session_service import SessionService
from core.config import settings
import asyncio
import json

# Instantiate singletons internally to prevent model reloads per request
rule_detector_inst = RuleDetector()
ml_detector_inst = MLDetector() if settings.USE_ML_DETECTOR else None
fake_gen_inst = FakeDataGenerator()
logging_svc_inst = LoggingService()
session_svc_inst = SessionService()

def get_honeypot_service():
    return HoneypotService(
        rule_detector=rule_detector_inst,
        ml_detector=ml_detector_inst,
        fake_gen=fake_gen_inst,
        logger=logging_svc_inst,
        session_svc=session_svc_inst
    )


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
        rule_result = self.rule_detector.classify(json.dumps(data))
        
        # Immediate fake response (don't block attacker)
        fake_resp = self.fake_gen.generate(data)
        
        # Async ML if rule conf high
        if rule_result.confidence > 0.6 and self.ml_detector:
            background_tasks.add_task(self.ml_detector.score, data)
        
        # Background log + session update
        background_tasks.add_task(
            self.logger.write_attack, data, rule_result, fake_resp
        )
        
        return fake_resp

