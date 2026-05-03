from fastapi import FastAPI, Depends, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from schemas import PostSchema, GroupAddRequest
from sqlalchemy.orm import Session, joinedload, selectinload
from app.db import crud, session
from app.db.models import Trend, Post, Industry
import schemas

from sqlalchemy import desc, text

from app.services import group_manager
from app.services import parser
from app.services import pipeline

from app.core.config import settings

parser = parser.VKParser(settings.VK_TOKEN)
pipeline = pipeline.AnalysisPipeline(settings.YANDEX_FOLDER_ID, settings.YANDEX_API_KEY)

app = FastAPI()

origins = [
    "http://localhost:5173",
    "https://vk-apps.com", 
    "https://vk.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            
    allow_credentials=True,           
    allow_methods=["*"],               
    allow_headers=["*"],               
)

@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Hello"}

# About page route
@app.get("/about")
def about() -> dict[str, str]:
    return {"message": "This is the about page."}

# Route to list all posts in db
@app.get("/posts", response_model=List[PostSchema])
def get_all_posts(
    limit: int = 50, 
    offset: int = 0, 
    category_ids: List[int] = Query(None), 
    db: Session = Depends(session.get_db)
):
    return crud.get_posts(
        db, 
        category_ids=category_ids, 
        limit=limit, 
        offset=offset
    )

@app.get("/groups", response_model=List[schemas.GroupSchema])
def get_channels(db: Session = Depends(session.get_db)):
    groups = crud.get_groups(db)
    return groups

@app.get("/categories", response_model=List[schemas.IndustrySchema])
def get_categories(db: Session = Depends(session.get_db)):
    return crud.get_all_industries(db)

@app.post("/parsing")
async def parse_sources(db: Session = Depends(session.get_db)):
    groups_in_db = crud.get_groups(db)
    urls = [c.url for c in groups_in_db]
    raw_posts = await parser.parse_multiple_groups(urls, db)

    return {
        "Статус": "успешно"
    }

@app.post("/text_analysis")
async def run_analysis(background_tasks: BackgroundTasks):
    background_tasks.add_task(pipeline.process_new_posts)

    return {
        "Статус": "анализ начался"
    }

# Route to list trends
@app.post("/trends")
async def trends_discover(db: Session = Depends(session.get_db)):

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
                    "Вовлеченность": p.er,
                    "Дата": p.posted_at
                } for p in related_posts
            ]
        })

    return {
    "Количество трендов": len(result),
    "Тренды": result
    }

@app.get("/Посты с категориями")
async def check_posts(db: Session = Depends(session.get_db)):
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
def get_average_stats(db: Session = Depends(session.get_db)):
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

@app.post("/groups/add", summary="Добавить новую группу")
async def add_group(payload: GroupAddRequest, db: Session = Depends(session.get_db)):
    manager = group_manager.GroupManager(db, settings.VK_TOKEN)
    new_group = await manager.add_group_by_url(payload.url)
    return new_group
    

