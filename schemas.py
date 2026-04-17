from typing import Optional, List
from pydantic import BaseModel, ConfigDict, field_validator, Field
from datetime import datetime
import numpy as np

class IndustrySchema(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class PostSchema(BaseModel):
    id: int
    group_id: int
    message_id: int
    text: str
    cleaned_text: Optional[str] = None  
    normalized_text: Optional[str] = None 
    posted_at: datetime
    likes_count: Optional[int] = 0 
    views_count : Optional[int] = 0 
    embedding: List[float]
    industry: List[IndustrySchema] = []

    # model_config = ConfigDict(from_attributes=True)

    @field_validator("embedding", mode="before")
    @classmethod
    def limit_vector(cls, v):
        if v is not None:
            if isinstance(v, np.ndarray):
                return v[:5].tolist()
            return list(v)[:5]
        return []
    
    class Config:
        from_attributes = True


class GroupSchema(BaseModel):
    id: int
    screen_name: str
    title: str

    model_config = ConfigDict(from_attributes=True)

class PostInTrendSchema(BaseModel):
    id: int
    text: str
    
    class Config:
        from_attributes = True 

class TrendDebugSchema(BaseModel):
    id: int
    name: str  # Вот тут мы будем видеть результат работы YandexGPT
    discovered_at: datetime
    posts_count: int
    posts: List[PostInTrendSchema]
    industry: List[IndustrySchema] = []

    class Config:
        from_attributes = True
