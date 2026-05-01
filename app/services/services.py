from sqlalchemy.orm import Session
from app.db.models import Group
import httpx
import logging

class VKService:
    def __init__(self, token: str):
        self.token = token
        self.api_version = "5.131"

    async def get_group_data(self, screen_name: str):
        async with httpx.AsyncClient() as client:
            params = {
                "group_ids": screen_name,
                "fields": "members_count, description",
                "access_token": self.token,
                "v": self.api_version
            }
            try:
                response = await client.get("https://api.vk.com/method/groups.getById", params=params)
                data = response.json()
                
                if "error" in data:
                    logging.error(f"VK API Error: {data['error']['error_msg']}")
                    return None
                
                return data["response"][0]
            except Exception as e:
                logging.error(f"Ошибка при запросе к VK: {e}")
                return None

