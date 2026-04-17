from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db import models


def get_channel_by_id(db: Session, channel_id: int) -> Optional[models.Channel]:
    return db.get(models.Channel, channel_id)


def get_channel_by_username(db: Session, username: str) -> Optional[models.Channel]:
    stmt = select(models.Channel).where(models.Channel.username == username)
    return db.scalar(stmt)


def get_channel_by_url(db: Session, url: str) -> Optional[models.Channel]:
    stmt = select(models.Channel).where(models.Channel.url == url)
    return db.scalar(stmt)


def list_channels(db: Session, skip: int = 0, limit: int = 100) -> List[models.Channel]:
    stmt = select(models.Channel).offset(skip).limit(limit)
    return db.scalars(stmt).all()


def create_channel(db: Session, username: str, url: str, title: Optional[str] = None) -> models.Channel:
    channel = models.Channel(username=username, url=url, title=title)
    db.add(channel)
    db.commit()
    db.refresh(channel)
    return channel


def get_industry_by_name(db: Session, name: str) -> Optional[models.Industry]:
    stmt = select(models.Industry).where(models.Industry.name == name)
    return db.scalar(stmt)


def list_industries(db: Session, skip: int = 0, limit: int = 100) -> List[models.Industry]:
    stmt = select(models.Industry).offset(skip).limit(limit)
    return db.scalars(stmt).all()


def create_industry(db: Session, name: str, description: Optional[str] = None) -> models.Industry:
    sphere = models.Industry(name=name, description=description)
    db.add(sphere)
    db.commit()
    db.refresh(sphere)
    return sphere


def get_or_create_industry(db: Session, name: str, description: Optional[str] = None) -> models.Industry:
    sphere = get_industry_by_name(db, name)
    if sphere:
        return sphere
    return create_industry(db, name=name, description=description)


def get_post_by_channel_and_message(db: Session, channel_id: int, message_id: int) -> Optional[models.Post]:
    stmt = select(models.Post).where(
        models.Post.channel_id == channel_id,
        models.Post.message_id == message_id,
    )
    return db.scalar(stmt)


def list_posts(db: Session, skip: int = 0, limit: int = 100) -> List[models.Post]:
    stmt = select(models.Post).offset(skip).limit(limit)
    return db.scalars(stmt).all()


def create_post(
    db: Session,
    channel: models.Channel,
    message_id: int,
    text: str,
    posted_at,
    industry_list: Optional[List[models.Industry]] = None,
) -> models.Post:
    post = models.Post(
        channel=channel,
        message_id=message_id,
        text=text,
        posted_at=posted_at,
    )
    if industry_list:
        post.industries = industry_list
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def get_trend_by_id(db: Session, trend_id: int) -> Optional[models.Trend]:
    return db.get(models.Trend, trend_id)


def list_trends(db: Session, skip: int = 0, limit: int = 100) -> List[models.Trend]:
    stmt = select(models.Trend).offset(skip).limit(limit)
    return db.scalars(stmt).all()


def list_trends_by_industry(db: Session, sphere_id: int, skip: int = 0, limit: int = 100) -> List[models.Trend]:
    stmt = select(models.Trend).where(models.Trend.sphere_id == sphere_id).offset(skip).limit(limit)
    return db.scalars(stmt).all()


def create_trend(
    db: Session,
    name: str,
    sphere: Optional[models.Industry] = None,
    description: Optional[str] = None,
    score: int = 0,
    posts: Optional[List[models.Post]] = None,
) -> models.Trend:
    trend = models.Trend(name=name, description=description, score=score, sphere=sphere)
    if posts:
        trend.posts = posts
    db.add(trend)
    db.commit()
    db.refresh(trend)
    return trend