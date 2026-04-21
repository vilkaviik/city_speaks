from fastapi import FastAPI, Depends, BackgroundTasks, APIRouter
from typing import List
from schemas import PostSchema
from schemas import GroupSchema
from sqlalchemy.orm import Session
from app.db.models import Group
from app.db.models import Trend
from app.db.models import Post
from app.db.models import Industry
from app.db.session import get_db

from sqlalchemy.orm import joinedload
from sqlalchemy.orm import selectinload
from sqlalchemy import desc

from app.services.parser import VKParser
from app.services.pipeline import AnalysisPipeline

from app.core.config import settings

from sqlalchemy import func, text
from datetime import datetime, timedelta

app = FastAPI()

parser = VKParser(settings.VK_TOKEN)
pipeline = AnalysisPipeline(settings.YANDEX_FOLDER_ID, settings.YANDEX_API_KEY)

@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Hello"}

# About page route
@app.get("/about")
def about() -> dict[str, str]:
    return {"message": "This is the about page."}

# Route to list all posts in db
@app.get("/Посты", response_model=List[PostSchema])
def get_all_posts(
    limit: int = 50, 
    offset: int = 0, 
    db: Session = Depends(get_db)
):
    posts = db.query(Post)\
    .options(selectinload(Post.industry))\
    .order_by(desc(Post.er))\
    .all()

    return posts

# Route to list all channels: username + url
@app.get("/Группы", response_model=List[GroupSchema])
def get_channels(db: Session = Depends(get_db)):
    channels = db.query(Group).all()
    #return {
    #"Количество групп": len(channels),
    #"Группы": channels
    #}

    return channels

# Route to trigger parsing
@app.post("/Парсинг")
async def parse_sources(db: Session = Depends(get_db)):

    groups_in_db = db.query(Group).all()
    urls = [c.url for c in groups_in_db]

    raw_posts = await parser.parse_multiple_groups(urls, db)

    return {
        "Статус": "успешно"
    }

@app.post("/Анализ текста")
async def run_analysis(background_tasks: BackgroundTasks):
    background_tasks.add_task(pipeline.process_new_posts)

    return {
        "Статус": "анализ начался"
    }

# Route to list trends
@app.post("/Тренды")
async def trends_discover(db: Session = Depends(get_db)):

    trends = db.query(Trend).options(joinedload(Trend.industry)).all()
    result = []

    for trend in trends:
        related_posts = trend.posts
        #industry_names = [ind.name for ind in trend.industry]
        result.append({
            "ID тренда": trend.id,
            "Название": trend.name,
            "Вовлеченность": trend.er,
            #"Категория": industry_names,
            "Количество постов": len(related_posts),
            "Посты": [
                {
                    "ID поста": p.id, 
                    "Текст": p.text[:100] + "...",
                    "Источник": p.group.title,
                    "Вовлеченность": p.er
                } for p in related_posts
            ]
        })

    return {
    "Количество трендов": len(result),
    "Тренды": result
    }

@app.get("/Посты с категориями")
async def check_posts(db: Session = Depends(get_db)):
    industry_debug = []
    industries = db.query(Industry).all()
    for i in industries:
        industry_debug.append({
            "ID категории": i.id,
            "Название": i.name,
            "Описание": i.description
        })

    posts = (
        db.query(Post)
        .options(joinedload(Post.industry)) # Загружаем связь Many-to-Many
        .order_by(Post.created_at.desc())
        .all()
    )
    debug_data = []
    for p in posts:
        industry_names = [ind.name for ind in p.industry]
        
        debug_data.append({
            "ID поста": p.id,
            "Текст": p.text[:50] + "...",
            "Категория": industry_names,
            "Векторизация": p.embedding is not None
        })

    return {
    "Категории": industry_debug, 
    "Количество постов": len(debug_data),
    "Посты": debug_data
    }

@app.get("/posts/average-stats")
def get_average_stats(db: Session = Depends(get_db)):
    def get_avg_query(hours_interval: int):
        query = text(f"""
            WITH intervals AS (
                SELECT count(*) as count_per_interval
                FROM posts
                GROUP BY date_trunc('day', posted_at), 
                         (EXTRACT(HOUR FROM posted_at)::int / {hours_interval})
            )
            SELECT AVG(count_per_interval) FROM intervals
        """)
        result = db.execute(query).scalar()
        return round(float(result or 0), 2)

    return {
        "avg_every_1_hour": get_avg_query(1),
        "avg_every_8_hours": get_avg_query(8),
        "avg_every_12_hours": get_avg_query(12)
    }


