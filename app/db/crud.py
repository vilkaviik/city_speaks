from typing import List, Optional
from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy import desc, and_, update
from app.db.models import Post, Group, Industry, Trend
from datetime import datetime, timedelta

## POSTS

def get_posts_with_industries(db: Session):
    return db.query(Post).options(selectinload(Post.industry)).all()

def get_posts(db: Session, category_ids: list[int] = None, group_ids: list[int] = None, limit: int = 50, offset: int = 0, sort: str = "new"):
    query = db.query(Post).options(
        selectinload(Post.industry),
        joinedload(Post.group) 
    )

    if category_ids:
        filtered_ids = [idx for idx in category_ids if idx != 0]
        if filtered_ids:
            query = query.filter(Post.industry.any(Industry.id.in_(filtered_ids)))
            
    if group_ids:
        query = query.filter(Post.group_id.in_(group_ids))

    if sort == "top":
        seven_days_ago = datetime.utcnow() - timedelta(days=7)

        query = query.filter(Post.posted_at >= seven_days_ago)\
                     .order_by(desc(Post.likes_count))

    else:
        query = query.order_by(Post.posted_at.desc())

    return query.offset(offset)\
                .limit(limit)\
                .all()

def add_post(db: Session, group_id: int, message_id: int, post_payload: dict):
    exists = db.query(Post).filter(
        Post.group_id == group_id,
        Post.message_id == message_id
    ).first()

    if not exists:
        new_post = Post(
            group_id=group_id, 
            message_id=message_id, 
            **post_payload
        )
        db.add(new_post)
    else:
        for key, value in post_payload.items():
            setattr(exists, key, value)
    db.commit()

def save_post(db: Session, post: Post):
    db.add(post)

def update_post(db: Session, post: Post, **kwargs):
    for key, value in kwargs.items():
        setattr(post, key, value)
    db.add(post)
    return post

def get_posts_by_period(db: Session, time_threshold: datetime):
    return db.query(Post).filter(
        and_(
            Post.posted_at >= time_threshold,
            Post.embedding != None
        )
    ).order_by(Post.created_at.desc()).all()


## INDUSTRIES

def get_all_industries(db: Session):
    return db.query(Industry).all()

def add_industry_to_post(db: Session, post: Post, industry: Industry):
    post.industry.append(industry)
    db.add(post)

def create_industry(db: Session, name: str, description: str):
    new_industry = Industry(name=name, description=description)
    db.add(new_industry)
    db.commit()
    db.refresh(new_industry)
    return new_industry

## GROUPS

def get_groups(db: Session):
    return db.query(Group).all()

def get_group_by_screen_name(db: Session, screen_name: str):
    return db.query(Group).filter(Group.screen_name == screen_name).first()

def create_group(db: Session, vk_data: dict, original_url: str):
    new_group = Group(
        vk_id=str(vk_data.get("id")),
        title=vk_data.get("name", "Unknown"),
        screen_name=vk_data.get("screen_name"),
        url=original_url,
        subscribers=vk_data.get("members_count", 0),
        avatar_path=vk_data.get("photo_200") 
    )
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    return new_group

def update_group_subscribers(db: Session, group: Group, count: int, avatar_url: str = None):
    group.subscribers = count
    if avatar_url:
        group.avatar_path = avatar_url
    db.flush() 

## TRENDS

def get_trend_by_id(db: Session, trend_id: int):
    return db.get(Trend, trend_id)

def create_trend(
    db: Session, 
    trend_title: str, 
    centroid: str, 
    industry_id: int, 
    trend_er: float,
    timespan=str
):
    now = datetime.utcnow()
    
    new_trend = Trend(
        name=trend_title, 
        centroid=centroid, 
        discovered_at=now,
        updated_at=now, 
        industry_id=industry_id,
        er=trend_er,
        timespan=timespan
    )
    
    try:
        db.add(new_trend)      
        db.commit()            
        db.refresh(new_trend)  
        return new_trend
    except Exception as e:
        db.rollback()          
        print(f"Ошибка при создании тренда: {e}")
        raise e
    
def get_all_trends(db: Session):
    return db.query(Trend).all() 

def get_active_trends(db: Session, hours: int = 24):
    threshold = datetime.utcnow() - timedelta(hours=hours)
    return db.query(Trend).filter(Trend.updated_at >= threshold).all()

def archive_expired_trends(db: Session, hours: int = 24):
    threshold = datetime.utcnow() - timedelta(hours=hours)
    
    stmt = (
        update(Trend.__table__)
        .where(Trend.__table__.c.updated_at < threshold)
        .where(Trend.__table__.c.is_active == True)
        .values(is_active=False)
    )
    
    result = db.execute(stmt)
    db.commit()
    return result.rowcount

def get_unprocessed_posts(db: Session, time_threshold: datetime, limit: int = 100):
    return db.query(Post).filter(
        Post.created_at >= time_threshold,
        Post.embedding.isnot(None),
        Post.trends == None
    ).limit(limit).all()




