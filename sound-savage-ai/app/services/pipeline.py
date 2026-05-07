"""
Content Pipeline Orchestrator
Demonstrates how services flow together
Pure logic orchestration - no DB, no async
"""

from dataclasses import dataclass
from typing import Optional
from app.services.idea_engine import IdeaEngine, ProcessedIdea
from app.services.hook_engine import HookEngine, GeneratedHook
from app.services.script_engine import ScriptEngine, StructuredScript
from app.services.analytics_engine import AnalyticsEngine, PostMetrics, PerformanceAnalysis


@dataclass
class ContentPipelineOutput:
    """Complete pipeline output"""
    idea: ProcessedIdea
    hooks: list
    script: StructuredScript
    pipeline_status: str = "complete"


class ContentPipeline:
    """
    Orchestrates full content generation pipeline
    Idea → Hook → Script
    """
    
    @staticmethod
    def execute_idea_stage(raw_input: str, source: str = "manual") -> Optional[ProcessedIdea]:
        """Stage 1: Process and validate idea"""
        idea = IdeaEngine.process(raw_input, source)
        return idea
    
    @staticmethod
    def execute_hook_stage(idea: ProcessedIdea, num_hooks: int = 8) -> list:
        """Stage 2: Generate hooks"""
        hooks = HookEngine.generate_all_types(idea.raw_input, num_hooks)
        return hooks
    
    @staticmethod
    def execute_script_stage(hook: GeneratedHook, idea: ProcessedIdea) -> StructuredScript:
        """Stage 3: Build script from hook"""
        script = ScriptEngine.build(
            hook=hook.text,
            idea_text=idea.raw_input,
            category=idea.category,
            pacing="medium"
        )
        return script
    
    @classmethod
    def execute_full_pipeline(
        cls,
        raw_input: str,
        source: str = "manual",
        num_hooks: int = 8
    ) -> Optional[ContentPipelineOutput]:
        """
        Execute complete pipeline: Idea → Hooks → Scripts
        Returns None if idea validation fails
        """
        
        # Stage 1: Process idea
        idea = cls.execute_idea_stage(raw_input, source)
        if not idea:
            return None
        
        # Stage 2: Generate hooks
        hooks = cls.execute_hook_stage(idea, num_hooks)
        if not hooks:
            return None
        
        # Stage 3: Generate primary script
        primary_hook = hooks[0]
        script = cls.execute_script_stage(primary_hook, idea)
        
        return ContentPipelineOutput(
            idea=idea,
            hooks=hooks,
            script=script,
            pipeline_status="complete"
        )


class LearningFeedbackLoop:
    """
    Feedback loop: Performance → Learning → Next Content
    Uses analytics to improve future content
    """
    
    @staticmethod
    def process_performance(
        metrics: PostMetrics,
        hook_used: str,
        idea_used: str,
        viral_threshold: float = 10.0
    ) -> PerformanceAnalysis:
        """Analyze performance and generate insights"""
        
        analysis = AnalyticsEngine.analyze(metrics, viral_threshold)
        return analysis
    
    @staticmethod
    def generate_next_content_based_on_performance(
        analysis: PerformanceAnalysis,
        original_hook: str,
        original_idea: str
    ) -> dict:
        """
        Use performance insights to generate next content
        Returns remix strategy and suggested ideas
        """
        from app.services.remix_engine import RemixEngine
        
        remix_type = analysis.suggested_remix_type
        
        # Generate remix hooks
        remixed_hooks = RemixEngine.remix_hook(original_hook, remix_type)
        remixed_idea = RemixEngine.remix_idea(original_idea, remix_type)
        
        return {
            "remix_type": remix_type,
            "remixed_hooks": remixed_hooks,
            "remixed_idea": remixed_idea,
            "hook_effectiveness": analysis.hook_effectiveness,
            "insights": analysis.key_insights
        }
    
    @classmethod
    def full_feedback_cycle(
        cls,
        metrics: PostMetrics,
        hook_used: str,
        idea_used: str,
        viral_threshold: float = 10.0
    ) -> dict:
        """
        Complete feedback cycle:
        1. Analyze performance
        2. Extract insights
        3. Generate remix strategy
        4. Suggest next content
        """
        
        analysis = cls.process_performance(
            metrics,
            hook_used,
            idea_used,
            viral_threshold
        )
        
        next_content = cls.generate_next_content_based_on_performance(
            analysis,
            hook_used,
            idea_used
        )
        
        return {
            "analysis": {
                "viral_score": analysis.viral_score,
                "is_high_performer": analysis.is_high_performer,
                "performance_tier": analysis.performance_tier,
                "insights": analysis.key_insights,
            },
            "next_steps": next_content
        }
