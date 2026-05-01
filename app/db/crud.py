from typing import List, Optional
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from app.db.models import Post, Group, Industry

def get_group_by_screen_name(db: Session, screen_name: str):
    return db.query(Group).filter(Group.screen_name == screen_name).first()

def get_posts_with_industries(db: Session):
    return db.query(Post).options(selectinload(Post.industry)).all()

def get_all_industries(db: Session):
    return db.query(Industry).all()

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

def add_industry_to_post(db: Session, post: Post, industry: Industry):
    post.industry.append(industry)
    db.add(post)

def create_group(db: Session, vk_data: dict, original_url: str):
    new_group = Group(
        vk_id=str(vk_data.get("id")),
        title=vk_data.get("name", "Unknown"),
        screen_name=vk_data.get("screen_name"),
        url=original_url,
        subscribers=vk_data.get("members_count", 0)
    )
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    return new_group

def update_group_subscribers(db: Session, group: Group, count: int):
    group.subscribers = count
    db.flush() 



