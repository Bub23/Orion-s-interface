"""
Content idea models
"""

from sqlalchemy import Column, String, Text, Float, ForeignKey, JSON, Boolean, Integer, DateTime
from app.core.database import BaseModel


class ContentIdea(BaseModel):
    __tablename__ = "content_ideas"

    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    source = Column(String, nullable=False)  # manual, trend, remix
    raw_input = Column(Text, nullable=False)
    
    category = Column(String)  # music, story, ai, brand
    viral_score = Column(Float, default=0.0)
    
    status = Column(String, default="pending")  # pending, processing, ready


class Hook(BaseModel):
    __tablename__ = "hooks"

    content_id = Column(String, ForeignKey("content_ideas.id"), nullable=False)
    
    hook_text = Column(Text, nullable=False)
    hook_type = Column(String, nullable=False)  # shock, emotional, authority, storytelling
    
    variants = Column(JSON, default={})  # Store hook variants
    performance_score = Column(Float, default=0.0)
    is_high_performer = Column(Boolean, default=False)
    times_used = Column(Integer, default=0)


class Script(BaseModel):
    __tablename__ = "scripts"

    content_id = Column(String, ForeignKey("content_ideas.id"), nullable=False)
    hook_id = Column(String, ForeignKey("hooks.id"), nullable=False)
    
    hook = Column(Text, nullable=False)
    body = Column(JSON, nullable=False)  # List of paragraphs/sections
    cta = Column(Text, nullable=False)
    
    pacing = Column(String)  # fast, medium, slow
    
    status = Column(String, default="pending")  # pending, ready, rendering


class RenderJob(BaseModel):
    __tablename__ = "render_jobs"

    script_id = Column(String, ForeignKey("scripts.id"), nullable=False)
    
    platform = Column(String, nullable=False)  # runway, heygen, synthesia
    style_template = Column(String)
    
    status = Column(String, default="queued")  # queued, processing, done, failed
    output_url = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)


class Post(BaseModel):
    __tablename__ = "posts"

    render_job_id = Column(String, ForeignKey("render_jobs.id"), nullable=False)
    
    platform = Column(String, nullable=False)  # youtube, tiktok, instagram, facebook
    platform_post_id = Column(String, nullable=True)
    
    status = Column(String, default="pending")  # pending, published, failed
    published_at = Column(DateTime, nullable=True)
