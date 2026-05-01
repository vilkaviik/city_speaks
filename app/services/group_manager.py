from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.services.services import VKService
from app.db import crud

class GroupManager:
    def __init__(self, db: Session, vk_token: str):
        self.db = db
        self.vk_service = VKService(vk_token)

    async def add_group_by_url(self, url: str):
        screen_name = url.strip('/').split('/')[-1]

        if crud.get_group_by_screen_name(self.db, screen_name):
            raise HTTPException(status_code=400, detail="Группа уже в базе")

        vk_data = await self.vk_service.get_group_data(screen_name)

        print(f"DEBUG VK DATA: {vk_data} (type: {type(vk_data)})")

        if not vk_data:
            raise HTTPException(status_code=404, detail="Группа не найдена в ВК")
        
        return crud.create_group(self.db, vk_data, url)
