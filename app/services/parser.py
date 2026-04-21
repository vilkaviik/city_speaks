from telethon import TelegramClient, events
import os
import logging
import httpx
import uuid
import asyncio
from pathlib import Path
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Post
from app.db.models import Group
from sqlalchemy.orm import Session
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.metrics_counter import get_post_metrics

class TelegramParser:
    def __init__(self, API_ID, API_HASH):
        self.client = TelegramClient('SESSION_NAME', API_ID, API_HASH)
        self.on_new_post_callback = None

    # Парсинг псоледних публикаций за 24 часа
    async def parse_multiple_channels(self, channel_urls: list, db: Session):
        await self.client.start()
        time_threshold = datetime.now(timezone.utc) - timedelta(hours=24)

        for url in channel_urls:
            try:
                username = url.strip('/').split('/')[-1].replace('@', '')
                channel = db.query(Group).filter(Group.username == username).first()

                if not channel:
                    logging.warning(f"Канал @{username} не найден в БД. Пропускаю.")
                    continue

                entity = await self.client.get_entity(username)

                async for message in self.client.iter_messages(username):

                    if message.date < time_threshold:
                        break
                    
                    if not message.text or not message.text.strip():
                        continue

                    if message.text:
                    # 2. Проверяем, нет ли уже такого сообщения (по message_id и channel_id)
                        exists = db.query(Post).filter(
                            Post.channel_id == channel.id,
                            Post.message_id == message.id
                        ).first()

                    if not exists:
                        new_post = Post(
                            channel_id=channel.id,
                            message_id=message.id,
                            text=message.text,
                            posted_at=message.date
                        )
                        db.add(new_post)

                db.commit()
                        
            except Exception as e:
                logging.error(f"Ошибка при парсинге {url}: {e}")
                continue
            
    # Функция для скачивания аватарки канала
    async def download_profile_pic(client, entity, channel_obj, db: Session):
        if not entity.photo:
            return

        current_photo_id = str(entity.photo.photo_id)

        # Проверка, поменялась ли аватарка
        if channel_obj.photo_id == current_photo_id and channel_obj.photo_path:
            return

        base_dir = "storage/avatars"
        os.makedirs(base_dir, exist_ok=True)

        file_name = f"{channel_obj.username}_{current_photo_id[:8]}.jpg" 
        file_path = os.path.join(base_dir, file_name)

        path = await client.download_profile_pic(entity, file=file_path)

        if path:
            channel_obj.photo_path = f"avatars/{file_name}"
            channel_obj.photo_id = current_photo_id
            db.commit()

class VKParser:
    def __init__(self, service_token: str):
        self.token = service_token
        self.api_version = "5.131"
        self.base_url = "https://vk.com"

    async def parse_multiple_groups(self, group_urls: list, db: Session):
        time_threshold = datetime.now(timezone.utc) - timedelta(hours=24)
        async with httpx.AsyncClient() as client:

            screen_names = [url.strip('/').split('/')[-1] for url in group_urls]
            all_counts = await self.get_all_subscribers(client, screen_names)

            for url in group_urls:
                try:
                    screen_name = url.strip('/').split('/')[-1]
                    group = db.query(Group).filter(Group.screen_name == screen_name).first()

                    if not group:
                        logging.warning(f"Группа {screen_name} не найдена в БД. Пропускаю.")
                        continue

                    count = all_counts.get(screen_name, 0)

                    group.subscribers = count
                    db.commit()

                    raw_id = int(group.vk_id)
                    clean_owner_id = -abs(raw_id)

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

                        likes, views, url = get_post_metrics(post)

                        exists = db.query(Post).filter(
                            Post.group_id == group.id,
                            Post.message_id == post["id"]
                        ).first()

                        er_value = (likes / group.subscribers * 100) if group.subscribers > 0 else 0

                        if not exists:
                            new_post = Post(
                                group_id=group.id,
                                message_id=post["id"],
                                text=post["text"],
                                posted_at=post_date,
                                likes_count=likes,
                                views_count=views,
                                url=url,
                                er=er_value
                            )
                            db.add(new_post)

                        else:
                            exists.likes_count = likes
                            exists.views_count = views
                            exists.post_url = url
                            exists.er = er_value

                    db.commit()
                    await asyncio.sleep(0.4) 

                except Exception as e:
                    logging.error(f"Ошибка при парсинге {url}: {e}")
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

    async def get_subscribers_count(self, client: httpx.AsyncClient, group_id: str) -> int:
        try:
            params = {
                "group_id": group_id,
                "fields": "members_count",
                "access_token": self.token.strip(),
                "v": self.api_version
            }
            response = await client.get("https://api.vk.com/method/groups.getById", params=params)
            data = response.json()

            if "response" in data and len(data["response"]) > 0:
                return data["response"][0].get("members_count", 0)
            
            print(f"Ошибка API VK при получении участников {group_id}: {data.get('error')}")
            return 0
        except Exception as e:
            print(f"Исключение при запросе участников для {group_id}: {e}")
            return 0

    async def get_all_subscribers(self, client: httpx.AsyncClient, screen_names: list) -> dict:
        try:
            params = {
                "group_ids": ",".join(screen_names),
                "fields": "members_count",
                "access_token": self.token.strip(),
                "v": self.api_version
            }
            response = await client.get("https://api.vk.com/method/groups.getById", params=params)
            data = response.json()

            if "response" in data:
                return {item['screen_name']: item.get('members_count', 0) for item in data['response']}
            
            return {}
        
        except Exception as e:
            logging.error(f"Ошибка при массовом получении участников: {e}")
            return {}
















        

