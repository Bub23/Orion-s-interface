"""
Subscription model
"""

from sqlalchemy import Column, String, Boolean, ForeignKey
from app.core.database import BaseModel


class Subscription(BaseModel):
    __tablename__ = "subscriptions"

    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    
    tier = Column(String, nullable=False)  # free, creator, music, empire
    is_active = Column(Boolean, default=True)
    
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
