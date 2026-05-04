from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table, BigInteger, UniqueConstraint, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.db.base import Base
from pgvector.sqlalchemy import Vector 

post_industry = Table(
    "post_industry",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("industry_id", Integer, ForeignKey("industries.id", ondelete="CASCADE"), primary_key=True),
)

trend_post = Table(
    "trend_post",
    Base.metadata,
    Column("trend_id", Integer, ForeignKey("trends.id", ondelete="CASCADE"), primary_key=True),
    Column("post_id", Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
)


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    vk_id = Column(BigInteger, unique=True, nullable=False, index=True)
    screen_name = Column(String(255), unique=True, nullable=False, index=True)
    subscribers = Column(Integer, default=0)
    title = Column(String(512), nullable=True)
    url = Column(String(1024), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    avatar_path = Column(String(1024), nullable=True)
    
    posts = relationship("Post", back_populates="group", cascade="all, delete-orphan")


class Industry(Base):
    __tablename__ = "industries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), unique=True, nullable=False, index=True)
    description = Column(String(512), nullable=True)

    posts = relationship("Post", secondary=post_industry, back_populates="industry")
    trends = relationship("Trend", back_populates="industry")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True)
    industry_id = Column(Integer, ForeignKey("industries.id", ondelete="SET NULL"), nullable=True, index=True)
    message_id = Column(BigInteger, nullable=False, index=True)
    text = Column(Text, nullable=False)
    posted_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    likes_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    url = Column(String, nullable=True)
    images = Column(JSONB, nullable=True, server_default='[]') 

    cleaned_text = Column(Text, nullable=True)
    normalized_text = Column(Text, nullable=True)
    embedding = Column(Vector(256), nullable=True)

    er = Column(Float, default=0)

    group = relationship("Group", back_populates="posts")
    industry = relationship("Industry", secondary=post_industry, back_populates="posts")
    trends = relationship("Trend", secondary=trend_post, back_populates="posts")

    __table_args__ = (
        UniqueConstraint('message_id', 'group_id', name='_group_message_uc'),
    )


class Trend(Base):
    __tablename__ = "trends"

    id = Column(Integer, primary_key=True, index=True)
    industry_id = Column(Integer, ForeignKey("industries.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String(256), nullable=False, index=True)
    centroid = Column(Vector(256), nullable=True)
    discovered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    er = Column(Float, default=0)

    industry = relationship("Industry", back_populates="trends")
    posts = relationship("Post", secondary=trend_post, back_populates="trends")


 