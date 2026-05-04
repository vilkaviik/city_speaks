import os
import logging
import httpx
import uuid
import asyncio
import traceback
from pathlib import Path
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import crud

from app.services.metrics_counter import get_post_metrics

class VKParser:
    def __init__(self, service_token: str):
        self.token = service_token
        self.api_version = "5.131"
        self.base_url = "https://vk.com"

    async def parse_multiple_groups(self, group_urls: list, db: Session):
        print(f"DEBUG: START PARSING. URLS: {group_urls}") 
        time_threshold = datetime.now(timezone.utc) - timedelta(hours=24)
        async with httpx.AsyncClient() as client:

            screen_names = [url.strip('/').split('/')[-1] for url in group_urls]
            group_data = await self.get_all_subscribers(client, screen_names)
            subscribers_count = {sn: data['count'] for sn, data in group_data.items()}
            group_avatar = {sn: data['photo'] for sn, data in group_data.items()}
            logging.info(f"DEBUG: type of all_counts: {type(subscribers_count)}, value: {subscribers_count}")

            for url in group_urls:
                try:
                    screen_name = url.strip('/').split('/')[-1]
                    group = crud.get_group_by_screen_name(db, screen_name)

                    if not group:
                        logging.warning(f"Группа {screen_name} не найдена в БД. Пропускаю.")
                        continue

                    crud.update_group_subscribers(
                        db, 
                        group, 
                        subscribers_count.get(screen_name, 0), 
                        group_avatar.get(screen_name)
                    )

                    clean_owner_id = -abs(int(group.vk_id))
                    params = {
                        "owner_id": clean_owner_id,
                        "access_token": self.token.strip(),
                        "v": self.api_version,
                        "count": 5
                    }
                
                    response = await client.get(
                        "https://api.vk.com/method/wall.get",  
                        params=params                     
                    )
                    
                    data = response.json()
                    posts = data["response"]["items"]

                    for post in posts:
                        post_date = datetime.fromtimestamp(post["date"], tz=timezone.utc)
                        if post_date < time_threshold or not post.get("text"):
                            continue

                        likes, views, post_url = get_post_metrics(post)
                        er_value = (likes / group.subscribers * 100) if group.subscribers > 0 else 0

                        image_urls = []
                        if "attachments" in post:
                            for att in post["attachments"]:
                                if att["type"] == "photo":
                                    sizes = att["photo"].get("sizes", [])
                                    if sizes:
                                        image_urls.append(sizes[-1]["url"])

                        post_payload = {
                        "text": post["text"],
                        "posted_at": post_date,
                        "likes_count": likes,
                        "views_count": views,
                        "url": post_url, 
                        "er": er_value,
                        "images": image_urls,
                        }

                        crud.add_post(
                            db=db, 
                            group_id=group.id, 
                            message_id=post["id"], 
                            post_payload=post_payload
                        )

                    db.commit()
                    await asyncio.sleep(0.4) 

                except Exception as e:
                    logging.error(f"Ошибка при парсинге {url}: {e}")
                    traceback.print_exc()
                    db.rollback()
                    continue

    async def save_group_avatar(url: str) -> str:
        storage_dir = Path("storage/profile_pics")
        storage_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{uuid.uuid4()}.jpg"
        filepath = storage_dir / filename

        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(response.content)
                return filename
        return None

    async def get_all_subscribers(self, client: httpx.AsyncClient, screen_names: list) -> dict:
        try:
            params = {
                "group_ids": ",".join(screen_names),
                "fields": "members_count, photo_200",
                "access_token": self.token.strip(),
                "v": self.api_version
            }
            response = await client.get("https://api.vk.com/method/groups.getById", params=params)
            data = response.json()

            if "response" in data:
                return {
                item['screen_name']: {
                    "name": item.get('name'),
                    "count": item.get('members_count', 0),
                    "photo": item.get('photo_200') # Прямая ссылка на CDN ВК
                } for item in data['response']
            }
            return {}
        
        except Exception as e:
            logging.error(f"Ошибка при массовом получении участников: {e}")
            return {}
















        

