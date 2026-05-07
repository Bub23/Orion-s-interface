"""
Analytics worker
Handles performance tracking and learning loop
Processes metrics asynchronously
"""

from app.workers.celery_app import celery_app
from app.services.analytics_engine import AnalyticsEngine, PostMetrics
from app.services.pipeline import LearningFeedbackLoop


@celery_app.task(bind=True, name="tasks.track_post_performance")
def track_post_performance(
    self,
    post_id: str,
    views: int,
    engagement: int,
    clicks: int,
    shares: int,
    comments: int,
    hook_used: str = None,
    idea_used: str = None
):
    """
    Track post performance metrics
    Calculate viral score, insights, trigger learning
    
    Args:
        post_id: ID of post being tracked
        views, engagement, clicks, shares, comments: Raw metrics
        hook_used: Hook text used (for learning)
        idea_used: Idea text used (for learning)
    
    Returns:
        Performance analysis and learning insights
    """
    
    try:
        self.update_state(state='PROCESSING', meta={'status': 'calculating'})
        
        # Calculate metrics
        metrics = AnalyticsEngine.calculate_metrics(
            views=views,
            engagement=engagement,
            clicks=clicks,
            shares=shares,
            comments=comments
        )
        
        # Analyze performance
        analysis = AnalyticsEngine.analyze(metrics, viral_threshold=10.0)
        
        result = {
            "post_id": post_id,
            "metrics": {
                "viral_score": analysis.viral_score,
                "retention_rate": metrics.retention_rate,
                "ctr": metrics.ctr,
                "performance_tier": analysis.performance_tier,
            },
            "is_high_performer": analysis.is_high_performer,
            "insights": analysis.key_insights,
            "suggested_remix_type": analysis.suggested_remix_type,
            "hook_effectiveness": analysis.hook_effectiveness
        }
        
        # Trigger learning loop if high performer
        if analysis.is_high_performer and hook_used and idea_used:
            learning_result = trigger_learning_loop.apply_async(
                args=[
                    post_id,
                    metrics.viral_score,
                    analysis.suggested_remix_type,
                    hook_used,
                    idea_used
                ]
            )
            result["learning_triggered"] = {
                "task_id": learning_result.id,
                "remix_type": analysis.suggested_remix_type
            }
        
        self.update_state(state='SUCCESS', meta={'status': 'complete'})
        
        return result
        
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        return {
            "status": "failed",
            "error": str(e),
            "post_id": post_id
        }


@celery_app.task(bind=True, name="tasks.trigger_learning_loop")
def trigger_learning_loop(
    self,
    post_id: str,
    viral_score: float,
    remix_type: str,
    hook_used: str,
    idea_used: str
):
    """
    Trigger learning loop when post goes viral
    Generate remixes and suggest next content
    
    Args:
        post_id: Post ID that triggered learning
        viral_score: Viral score that triggered this
        remix_type: Suggested remix type
        hook_used: Original hook text
        idea_used: Original idea text
    
    Returns:
        Learning output with remixes and suggestions
    """
    
    try:
        self.update_state(state='PROCESSING', meta={'status': 'generating_remixes'})
        
        # Create mock metrics for feedback loop
        metrics = PostMetrics(
            views=1000,
            engagement=100,
            clicks=50,
            shares=20,
            comments=30,
            viral_score=viral_score
        )
        
        # Run feedback cycle
        feedback = LearningFeedbackLoop.full_feedback_cycle(
            metrics=metrics,
            hook_used=hook_used,
            idea_used=idea_used,
            viral_threshold=10.0
        )
        
        result = {
            "post_id": post_id,
            "learning_status": "complete",
            "analysis": feedback["analysis"],
            "next_steps": feedback["next_steps"],
            "remixes_generated": len(feedback["next_steps"].get("remixed_hooks", [])),
            "suggestion": f"Use {remix_type} strategy for next content batch"
        }
        
        self.update_state(state='SUCCESS', meta=result)
        
        return result
        
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        return {
            "status": "failed",
            "error": str(e),
            "post_id": post_id
        }


@celery_app.task(name="tasks.aggregate_daily_stats")
def aggregate_daily_stats(user_id: str):
    """
    Aggregate performance stats for the day
    
    Args:
        user_id: User to aggregate stats for
    
    Returns:
        Daily performance summary
    """
    
    try:
        # In production, query performance_events table
        # For now, return mock
        return {
            "user_id": user_id,
            "date": "today",
            "total_posts": 5,
            "avg_viral_score": 15.3,
            "high_performers": 2,
            "total_views": 25000,
            "engagement_rate": 12.5
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }
