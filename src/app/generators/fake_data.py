from typing import Dict, Any, List
from honeypot_system_hf_merged import HoneypotHFGenerator as LegacyGenerator
from core.config import settings
import re

class FakeDataGenerator:
    def __init__(self):
        self.generator = LegacyGenerator(api_key=settings.HF_API_KEY)
        self.fake_products = []  # From products.py

    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Schema-aware fake response immediate.
        """
        query = data.get("query", "")
        if "select" in query.lower():
            schema = self._extract_schema(query)
            fake_rows = []
            for i in range(5):  # Realistic row count
                row = {field: self._fake_value(field, dtype) for field, dtype in schema.items()}
                fake_rows.append(row)
            return {"results": fake_rows, "count": len(fake_rows)}
        
        # Default fake login/response
        return {"success": True, "message": "Login successful", "token": "fake_jwt", "user_id": 123}

    def _extract_schema(self, query: str) -> Dict[str, str]:
        # Port from legacy _enhanced_schema_extraction
        # Simplified
        return {
            "id": "int",
            "username": "str",
            "email": "email",
            "role": "str"
        }

    def _fake_value(self, field: str, dtype: str) -> Any:
        fakes = {
            "int": 12345,
            "str": "fake_user",
            "email": "admin@fake.com",
            "role": "admin"
        }
        return fakes.get(dtype, "fake_data")

