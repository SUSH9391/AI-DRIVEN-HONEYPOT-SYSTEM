from typing import Optional, Dict, Any
import httpx

class GeoService:
    def __init__(self):
        self.api_url = "http://ip-api.com/json/{ip}?fields=status,message,country,asn"

    async def enrich_ip(self, ip: str) -> Dict[str, Any]:
        """
        GeoIP enrichment background task.
        """
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(self.api_url.format(ip=ip))
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("status") == "success":
                        return {
                            "country": data.get("country"),
                            "asn": data.get("asn")
                        }
        except:
            pass
        return {"country": None, "asn": None}

