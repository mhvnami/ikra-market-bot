import os
import aiohttp
from dotenv import load_dotenv

load_dotenv()

CDEK_CLIENT_ID = os.getenv("CDEK_CLIENT_ID")
CDEK_CLIENT_SECRET = os.getenv("CDEK_CLIENT_SECRET")


async def get_cdek_token():
    url = "https://api.cdek.ru/v2/oauth/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": CDEK_CLIENT_ID,
        "client_secret": CDEK_CLIENT_SECRET
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            data = await response.json()
            return data.get("access_token")


async def calculate_delivery_price(token, from_city_code, to_city_code, weight_grams):
    url = "https://api.cdek.ru/v2/calculator/tariff"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    payload = {
        "type": 1,
        "currency": 1,
        "tariff_code": 136,  # Тариф: Склад-Склад (эконом)
        "from_location": {"code": from_city_code},
        "to_location": {"code": to_city_code},
        "packages": [{"weight": weight_grams}]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            return await response.json()


async def get_pickup_points(city_code, token):
    url = f"https://api.cdek.ru/v2/deliverypoints?city_code={city_code}"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return await response.json()
