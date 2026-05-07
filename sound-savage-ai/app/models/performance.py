"""
Performance tracking model
"""

from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime
from datetime import datetime
from app.core.database import BaseModel


class PerformanceEvent(BaseModel):
    __tablename__ = "performance_events"

    post_id = Column(String, ForeignKey("posts.id"), nullable=False)
    content_id = Column(String, ForeignKey("content_ideas.id"), nullable=False)
    
    views = Column(Integer, default=0)
    engagement = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    
    retention_rate = Column(Float, default=0.0)
    ctr = Column(Float, default=0.0)
    viral_score = Column(Float, default=0.0)
    
    hook_tag = Column(String)  # VIRAL_TRIGGER, HIGH_RETENTION, EMOTIONAL_SPIKE, STORY_WINNER
    
    tracked_at = Column(DateTime, default=datetime.utcnow)
