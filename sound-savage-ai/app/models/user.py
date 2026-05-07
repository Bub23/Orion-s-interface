"""
User model
"""

from sqlalchemy import Column, String, Boolean
from app.core.database import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    
    subscription_status = Column(String, default="free")  # free, creator, music, empire
    
    is_active = Column(Boolean, default=True)
