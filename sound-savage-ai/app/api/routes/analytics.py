"""
Analytics routes
POST /analytics/track - Track post performance
GET /analytics/learning/{post_id} - Get learning insights
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.api.deps import get_current_user_id
from app.workers.analytics_worker import (
    track_post_performance,
    trigger_learning_loop,
    aggregate_daily_stats
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


class TrackPerformanceRequest(BaseModel):
    post_id: str
    views: int
    engagement: int
    clicks: int
    shares: int
    comments: int
    hook_used: str = None
    idea_used: str = None


class TrackPerformanceResponse(BaseModel):
    task_id: str
    status: str
    message: str


class LearningInsightsResponse(BaseModel):
    post_id: str
    task_id: str
    status: str
    learning_status: str = None
    analysis: dict = None
    next_steps: dict = None
    error: str = None


class DailyStatsResponse(BaseModel):
    user_id: str
    date: str
    total_posts: int
    avg_viral_score: float
    high_performers: int
    total_views: int
    engagement_rate: float


@router.post("/track", response_model=TrackPerformanceResponse)
async def track_performance(
    request: TrackPerformanceRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Track post performance metrics"""
    
    # Queue analytics tracking task
    task = track_post_performance.apply_async(
        args=[
            request.post_id,
            request.views,
            request.engagement,
            request.clicks,
            request.shares,
            request.comments,
            request.hook_used,
            request.idea_used
        ],
        queue="analytics"
    )
    
    return TrackPerformanceResponse(
        task_id=task.id,
        status="queued",
        message="Performance metrics being processed"
    )


@router.get("/learning/{post_id}", response_model=LearningInsightsResponse)
async def get_learning_insights(
    post_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get learning insights for a post"""
    
    # In production, query learning_results table
    # For now, return placeholder
    return LearningInsightsResponse(
        post_id=post_id,
        task_id="learning_queued",
        status="pending",
        learning_status="Learning system will generate insights when post metrics are available"
    )


@router.get("/daily-stats", response_model=DailyStatsResponse)
async def get_daily_stats(user_id: str = Depends(get_current_user_id)):
    """Get daily performance stats"""
    
    # Queue daily aggregation task
    task = aggregate_daily_stats.apply_async(
        args=[user_id],
        queue="analytics"
    )
    
    # For now, return pending
    return DailyStatsResponse(
        user_id=user_id,
        date="today",
        total_posts=0,
        avg_viral_score=0.0,
        high_performers=0,
        total_views=0,
        engagement_rate=0.0
    )
