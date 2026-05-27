from fastapi import FastAPI, Depends, BackgroundTasks, Query, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, RedirectResponse
from typing import List, Optional
from schemas import PostSchema, GroupAddRequest, IndustryCreateRequest, IndustrySchema
from sqlalchemy.orm import Session, joinedload
from app.db import crud, session
from app.db.models import Trend, Post, Industry, Group
import schemas
import traceback
import io
from io import StringIO
import json
import pandas as pd
from sqlalchemy import desc, text
from datetime import datetime

from app.services import group_manager
from app.services import parser
from app.services import pipeline
from app.services.trend_discover import TrendDiscover
from app.services.export import ExportService

from app.core.config import settings

parser = parser.VKParser(settings.VK_TOKEN)
pipeline = pipeline.AnalysisPipeline(settings.YANDEX_FOLDER_ID, settings.YANDEX_API_KEY)
trend_service = TrendDiscover(settings.YANDEX_API_KEY, settings.YANDEX_FOLDER_ID)

app = FastAPI()

MODELS_MAP = {
    "trends": Trend,
    "posts": Post,
    "industries": Industry,
    "groups": Group
}

origins = [
    "https://vilkaviik-city-speaks-ec4f.twc1.net/",
    "http://localhost:3000",
    "https://vk-apps.com", 
    "https://vk.com",
    "https://user-api.com", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            
    allow_credentials=True,           
    allow_methods=["*"],               
    allow_headers=["*"],               
)

@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

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
    group_ids: list[int] = Query(None),
    sort: str = "new",
    db: Session = Depends(session.get_db)
):
    return crud.get_posts(
        db, 
        category_ids=category_ids, 
        group_ids=group_ids,
        limit=limit, 
        offset=offset,
        sort=sort
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
@app.get("/trends")
async def trends_discover(
    category_ids: Optional[List[int]] = Query(None), 
    timespan: str = Query("24h"),
    db: Session = Depends(session.get_db)
):
    query = db.query(Trend).options(
        joinedload(Trend.industry),
        joinedload(Trend.posts).joinedload(Post.group))
    
    query = query.filter(Trend.timespan == timespan)

    if category_ids:
        ids = [int(x) for x in category_ids]
        query = query.filter(Trend.industry_id.in_(ids))

    query = query.order_by(Trend.updated_at.desc())
    trends = query.all()

    result = []
    for trend in trends:
        result.append({
            "id": trend.id,
            "name": trend.name,
            "timespan": trend.timespan,
            "er": trend.er,
            "is_active": trend.is_active,  
            "industry": [{"id": trend.industry.id, "name": trend.industry.name}] if trend.industry is not None else [],
            "posts_count": len(trend.posts),
            "posts": [
                {
                    "id": p.id, 
                    "text": p.text, 
                    "er": p.er,
                    "likes_count": p.likes_count,
                    "views_count": p.views_count,
                    "date": p.posted_at.isoformat() if p.posted_at else None, 
                    "group": {
                        "name": p.group.title if p.group else "Unknown",
                        "url": p.group.url if p.group else "#",
                        "avatar_path": p.group.avatar_path if p.group else None
                    }
                } for p in trend.posts
            ]
        })

    return {
        "timespan_filter": timespan,
        "trends_count": len(result),
        "trends": result
    }

@app.get("/refresh_long_trends")
async def refresh_trends(db: Session = Depends(session.get_db)):
    try:
        # Проверь, как именно называется объект: self.trend_discover, pipeline.trend_discover или просто trend_discover
        await trend_service.discover_trends(db, days=1)
        await trend_service.discover_trends(db, days=3)
        await trend_service.discover_trends(db, days=7)
        
        return {"status": "success"}
    except Exception as e:
        # Это выведет подробности ошибки в консоль сервера
        print(traceback.format_exc()) 
        raise HTTPException(status_code=500, detail=str(e))


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

## SETTINGS

@app.post("/groups/add", summary="Добавить новую группу")
async def add_group(payload: GroupAddRequest, db: Session = Depends(session.get_db)):
    manager = group_manager.GroupManager(db, settings.VK_TOKEN)
    new_group = await manager.add_group_by_url(payload.url)
    return new_group

@app.post("/industries/add", summary="Добавить категорию")
async def add_industry(payload: IndustryCreateRequest, db: Session = Depends(session.get_db)):
    new_industry = crud.create_industry(db, payload.name, payload.description)
    return new_industry
    
@app.post("/update_prompt_in_trends")
async def update_llm_settings(new_prompt: str):
    try:
        settings.TREND_NAMING_PROMPT=new_prompt
        
        return {"status": "success", "message": "Prompt updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/reset_prompt_in_trends")
async def reset_llm_settings():
    settings.TREND_NAMING_PROMPT = settings.DEFAULT_TREND_PROMPT
    return {"message": "Сброшено до заводских настроек"}

def get_trends_data(db: Session):
    trends = db.query(Trend).options(joinedload(Trend.posts)).all()
    data = []
    for t in trends:
        data.append({
            "id": t.id,
            "name": t.name,
            "er": t.er,
            "posts_count": len(t.posts),
            "industry": t.industry.name if t.industry else "None"
        })
    return data

@app.get("/trends/{format}")
async def export_trends(format: str, db: Session = Depends(session.get_db)):
    data = get_trends_data(db)
    
    if format == "json":
        content = json.dumps(data, ensure_ascii=False, indent=4)
        return Response(content=content, media_type="application/json", 
                        headers={"Content-Disposition": "attachment; filename=trends.json"})
    
    elif format == "csv":
        df = pd.DataFrame(data)
        stream = io.StringIO()
        df.to_csv(stream, index=False)
        return Response(content=stream.getvalue(), media_type="text/csv", 
                        headers={"Content-Disposition": "attachment; filename=trends.csv"})

    elif format == "sql":
        lines = ["CREATE TABLE IF NOT EXISTS trends_export (id INT, name TEXT, er FLOAT, posts_count INT, industry TEXT);"]
        for d in data:
            val = f"({d['id']}, '{d['name']}', {d['er']}, {d['posts_count']}, '{d['industry']}');"
            lines.append(f"INSERT INTO trends_export VALUES {val}")
        content = "\n".join(lines)
        return Response(content=content, media_type="application/sql", 
                        headers={"Content-Disposition": "attachment; filename=trends.sql"})


@app.get("/export/{table_name}")
async def export_data(
    table_name: str,
    fields: list[str] = Query(None),
    format: str = "json",
    industry_id: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(session.get_db)
):
    if table_name not in MODELS_MAP:
        raise HTTPException(status_code=404, detail="Table not found")

    model = MODELS_MAP[table_name]
    query = db.query(model)

    if industry_id and hasattr(model, 'industry_id'):
        query = query.filter(model.industry_id == industry_id)

    date_field = None
    if table_name == "trends":
        date_field = model.discovered_at
    elif table_name == "posts":
        date_field = model.posted_at
    elif table_name == "groups":
        date_field = model.created_at

    if date_field is not None:
        if date_from:
            query = query.filter(date_field >= date_from)
        if date_to:
            query = query.filter(date_field <= date_to)

    items = query.all()
    selected_fields = fields or ExportService.DEFAULT_FIELDS.get(table_name, ["id"])
    clean_data = [ExportService.prepare_row(item, selected_fields) for item in items]

    if format == "sql":
        content = ExportService.to_sql(clean_data, table_name)
        return StreamingResponse(
            StringIO(content),
            media_type="application/sql",
            headers={"Content-Disposition": f"attachment; filename={table_name}.sql"}
        )
    else:
        content = json.dumps(clean_data, ensure_ascii=False, indent=2)
        media_type = "application/json"
        filename = f"{table_name}.json"


    return StreamingResponse(
        StringIO(content),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )