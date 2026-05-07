"""
Analytics Engine - Performance feedback loop
Calculates metrics and feeds learning systems
NO database access, NO async, pure calculations
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class PostMetrics:
    """Raw metrics from a published post"""
    views: int
    engagement: int
    clicks: int
    shares: int
    comments: int
    retention_rate: float = 0.0
    ctr: float = 0.0
    viral_score: float = 0.0


@dataclass
class PerformanceAnalysis:
    """Analyzed performance with insights"""
    viral_score: float
    is_high_performer: bool
    performance_tier: str  # "low", "medium", "high", "viral"
    key_insights: List[str]
    suggested_remix_type: str
    hook_effectiveness: float


class AnalyticsEngine:
    """
    Analyzes post performance
    Calculates metrics and identifies patterns
    Pure logic - no DB, no async
    """
    
    @staticmethod
    def calculate_metrics(
        views: int,
        engagement: int,
        clicks: int,
        shares: int,
        comments: int
    ) -> PostMetrics:
        """Calculate derived metrics from raw numbers"""
        
        # Avoid division by zero
        if views == 0:
            return PostMetrics(
                views=0,
                engagement=0,
                clicks=0,
                shares=shares,
                comments=comments,
                retention_rate=0.0,
                ctr=0.0,
                viral_score=0.0
            )
        
        # Retention rate: engagement as % of views
        retention_rate = (engagement / views) * 100
        
        # CTR: clicks as % of views
        ctr = (clicks / views) * 100
        
        # Viral score: (shares + comments) / views * 1000
        # Higher shares/comments relative to views = more viral
        viral_score = ((shares + comments) / views) * 1000
        
        return PostMetrics(
            views=views,
            engagement=engagement,
            clicks=clicks,
            shares=shares,
            comments=comments,
            retention_rate=round(retention_rate, 2),
            ctr=round(ctr, 2),
            viral_score=round(viral_score, 2)
        )
    
    @staticmethod
    def categorize_performance(viral_score: float) -> str:
        """Categorize post performance"""
        if viral_score >= 50:
            return "viral"
        elif viral_score >= 20:
            return "high"
        elif viral_score >= 5:
            return "medium"
        else:
            return "low"
    
    @staticmethod
    def is_high_performer(viral_score: float, threshold: float = 10.0) -> bool:
        """Determine if post meets high performer threshold"""
        return viral_score >= threshold
    
    @staticmethod
    def extract_insights(metrics: PostMetrics) -> List[str]:
        """Extract actionable insights from metrics"""
        insights = []
        
        if metrics.viral_score >= 50:
            insights.append("Extremely viral - this pattern needs to be remixed")
        elif metrics.viral_score >= 20:
            insights.append("High virality - strong performer")
        elif metrics.viral_score >= 10:
            insights.append("Good engagement - consider remixing this approach")
        
        if metrics.retention_rate > 40:
            insights.append("Strong retention - people are staying engaged")
        elif metrics.retention_rate < 5:
            insights.append("Low retention - hook may need adjustment")
        
        if metrics.ctr > 10:
            insights.append("High CTR - strong call-to-action")
        
        if metrics.shares > metrics.comments:
            insights.append("Share-focused content - good for reach")
        else:
            insights.append("Comment-focused - good for algorithm")
        
        return insights if insights else ["Content performed at baseline level"]
    
    @staticmethod
    def estimate_hook_effectiveness(metrics: PostMetrics) -> float:
        """
        Estimate how effective the hook was
        Based on early engagement metrics
        """
        if metrics.views == 0:
            return 0.0
        
        # Higher engagement early = better hook
        engagement_ratio = metrics.engagement / metrics.views
        
        # Normalize to 0-1
        effectiveness = min(engagement_ratio * 10, 1.0)
        
        return round(effectiveness, 2)
    
    @classmethod
    def suggest_remix_type(cls, metrics: PostMetrics, performance_tier: str) -> str:
        """Suggest which remix strategy to use"""
        
        if performance_tier == "viral":
            return "escalation"  # Push harder on what worked
        elif performance_tier == "high":
            return "variation"  # Safely iterate
        elif performance_tier == "medium":
            return "reframe"  # Try different angle
        else:
            return "variation"  # Start over cautiously
    
    @classmethod
    def analyze(
        cls,
        metrics: PostMetrics,
        viral_threshold: float = 10.0
    ) -> PerformanceAnalysis:
        """
        Full performance analysis pipeline
        """
        performance_tier = cls.categorize_performance(metrics.viral_score)
        is_high = cls.is_high_performer(metrics.viral_score, viral_threshold)
        insights = cls.extract_insights(metrics)
        hook_effectiveness = cls.estimate_hook_effectiveness(metrics)
        remix_type = cls.suggest_remix_type(metrics, performance_tier)
        
        analysis = PerformanceAnalysis(
            viral_score=metrics.viral_score,
            is_high_performer=is_high,
            performance_tier=performance_tier,
            key_insights=insights,
            suggested_remix_type=remix_type,
            hook_effectiveness=hook_effectiveness
        )
        
        return analysis
    
    @staticmethod
    def aggregate_performance(analyses: List[PerformanceAnalysis]) -> Dict:
        """Aggregate performance across multiple posts"""
        if not analyses:
            return {}
        
        total_viral = sum(a.viral_score for a in analyses)
        avg_viral = total_viral / len(analyses)
        high_performers = sum(1 for a in analyses if a.is_high_performer)
        
        return {
            "total_posts": len(analyses),
            "avg_viral_score": round(avg_viral, 2),
            "high_performers": high_performers,
            "success_rate": round((high_performers / len(analyses)) * 100, 1),
            "most_common_tier": max(
                set(a.performance_tier for a in analyses),
                key=[a.performance_tier for a in analyses].count
            )
        }
