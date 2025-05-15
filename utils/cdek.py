import os
import aiohttp
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

CDEK_CLIENT_ID = os.getenv("CDEK_CLIENT_ID")
CDEK_CLIENT_SECRET = os.getenv("CDEK_CLIENT_SECRET")

BASE_URL = "https://api.cdek.ru/v2"


class CDEKClient:
    def __init__(self):
        self.token: Optional[str] = None
        self.session = aiohttp.ClientSession()

    async def close(self):
        await self.session.close()

    async def get_token(self) -> Optional[str]:
        url = f"{BASE_URL}/oauth/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": CDEK_CLIENT_ID,
            "client_secret": CDEK_CLIENT_SECRET
        }

        try:
            async with self.session.post(url, json=payload) as response:
                data = await response.json()
                self.token = data.get("access_token")
                return self.token
        except Exception as e:
            print(f"[ERROR] Failed to get CDEK token: {e}")
            return None

    async def _ensure_token(self):
        if not self.token:
            await self.get_token()

    async def calculate_delivery_price(self, from_city_code: int, to_city_code: int, weight_grams: int) -> dict:
        await self._ensure_token()
        url = f"{BASE_URL}/calculator/tariff"
        headers = {"Authorization": f"Bearer {self.token}"}

        payload = {
            "type": 1,
            "currency": 1,
            "tariff_code": 136,
            "from_location": {"code": from_city_code},
            "to_location": {"code": to_city_code},
            "packages": [{"weight": weight_grams}]
        }

        try:
            async with self.session.post(url, headers=headers, json=payload) as response:
                return await response.json()
        except Exception as e:
            print(f"[ERROR] Failed to calculate delivery price: {e}")
            return {}

    async def get_pickup_points(self, city_code: int) -> dict:
        await self._ensure_token()
        url = f"{BASE_URL}/deliverypoints?city_code={city_code}"
        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            async with self.session.get(url, headers=headers) as response:
                return await response.json()
        except Exception as e:
            print(f"[ERROR] Failed to fetch pickup points: {e}")
            return {}
        
    async def create_shipment(
        self,
        sender_city_code: int,
        receiver_city_code: int,
        receiver_address: str,
        receiver_name: str,
        receiver_phone: str,
        package_weight: int = 500,
        length: int = 10,
        width: int = 10,
        height: int = 10,
        order_number: str = "ORDER-001"
    ) -> dict:
        await self._ensure_token()
        url = f"{BASE_URL}/orders"
        headers = {"Authorization": f"Bearer {self.token}"}

        payload = {
            "type": 1,
            "number": order_number,
            "comment": "Заявка создана через Telegram",
            "sender_city_code": sender_city_code,
            "receiver_city_code": receiver_city_code,
            "recipient": {
                "name": receiver_name,
                "phones": [{"number": receiver_phone}]
            },
            "delivery_point": receiver_address,
            "tariff_code": 136,
            "packages": [{
                "number": "P001",
                "weight": package_weight,
                "length": length,
                "width": width,
                "height": height
            }]
        }

        try:
            async with self.session.post(url, headers=headers, json=payload) as response:
                return await response.json()
        except Exception as e:
            print(f"[ERROR] Failed to create shipment: {e}")
            return {}    
