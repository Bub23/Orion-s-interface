"""
Test service engines
Demonstrates full pipeline execution
Run: python -m pytest app/services/test_services.py -v
"""

import pytest
from app.services.idea_engine import IdeaEngine
from app.services.hook_engine import HookEngine
from app.services.script_engine import ScriptEngine
from app.services.remix_engine import RemixEngine
from app.services.analytics_engine import AnalyticsEngine, PostMetrics
from app.services.pipeline import ContentPipeline, LearningFeedbackLoop
from app.services.scoring import ScoringEngine, CategoryScorer


class TestIdeaEngine:
    """Test idea processing"""
    
    def test_validate_input(self):
        """Test input validation"""
        assert IdeaEngine.validate_input("This is a valid idea with enough words") == True
        assert IdeaEngine.validate_input("short") == False
        assert IdeaEngine.validate_input("") == False
    
    def test_categorize(self):
        """Test categorization"""
        music_idea = "I made a beat that changed everything about rap production"
        category = IdeaEngine.categorize(music_idea)
        assert category == "music"
    
    def test_process(self):
        """Test full idea processing"""
        raw = "I lost everything when the market crashed but here's what I learned"
        idea = IdeaEngine.process(raw)
        
        assert idea is not None
        assert idea.raw_input == raw
        assert idea.source == "manual"
        assert idea.viral_score > 0
        assert idea.category in ["story", "hustle", "ai", "music", "brand"]


class TestHookEngine:
    """Test hook generation"""
    
    def test_generate_for_type(self):
        """Test single-type hook generation"""
        idea = "AI just replaced 3 jobs in one second"
        hooks = HookEngine.generate_for_type(idea, "shock", count=2)
        
        assert len(hooks) == 2
        assert all(h.hook_type == "shock" for h in hooks)
        assert all(h.text for h in hooks)
    
    def test_generate_all_types(self):
        """Test multi-type hook generation"""
        idea = "This is a viral story about making money"
        hooks = HookEngine.generate_all_types(idea, total_hooks=8)
        
        assert len(hooks) <= 8
        assert all(h.text for h in hooks)
        assert all(h.hook_type in ["shock", "story", "authority", "confession"] for h in hooks)


class TestScriptEngine:
    """Test script building"""
    
    def test_estimate_duration(self):
        """Test duration estimation"""
        duration = ScriptEngine.estimate_duration_for_words(100)
        assert duration > 0
        assert duration < 60  # Should be under 1 minute for 100 words
    
    def test_build_script(self):
        """Test full script building"""
        hook = "I lost everything in 24 hours"
        idea = "The story of my startup failure"
        category = "story"
        
        script = ScriptEngine.build(hook, idea, category)
        
        assert script.hook == hook
        assert script.category == category
        assert len(script.sections) > 0
        assert script.total_duration > 0
        assert script.cta


class TestRemixEngine:
    """Test remix generation"""
    
    def test_remix_hook_variation(self):
        """Test hook variation remix"""
        hook = "I lost everything"
        variants = RemixEngine.remix_hook(hook, "variation")
        
        assert len(variants) > 1
        assert hook in variants or any(hook in v for v in variants)
    
    def test_remix_idea_sequel(self):
        """Test idea remix"""
        idea = "How to make money online"
        remixed = RemixEngine.remix_idea(idea, "sequel")
        
        assert "Part 2" in remixed


class TestAnalyticsEngine:
    """Test performance analytics"""
    
    def test_calculate_metrics(self):
        """Test metric calculation"""
        metrics = AnalyticsEngine.calculate_metrics(
            views=1000,
            engagement=100,
            clicks=50,
            shares=20,
            comments=30
        )
        
        assert metrics.retention_rate == 10.0
        assert metrics.ctr == 5.0
        assert metrics.viral_score > 0
    
    def test_categorize_performance(self):
        """Test performance categorization"""
        assert AnalyticsEngine.categorize_performance(60) == "viral"
        assert AnalyticsEngine.categorize_performance(25) == "high"
        assert AnalyticsEngine.categorize_performance(10) == "medium"
        assert AnalyticsEngine.categorize_performance(2) == "low"
    
    def test_is_high_performer(self):
        """Test high performer threshold"""
        assert AnalyticsEngine.is_high_performer(15, 10) == True
        assert AnalyticsEngine.is_high_performer(5, 10) == False


class TestContentPipeline:
    """Test full pipeline execution"""
    
    def test_idea_stage(self):
        """Test pipeline idea stage"""
        raw = "I made a million dollars through AI automation in 90 days"
        idea = ContentPipeline.execute_idea_stage(raw)
        
        assert idea is not None
        assert idea.raw_input == raw
    
    def test_full_pipeline(self):
        """Test complete pipeline"""
        raw = "This is my story about building a successful startup from zero"
        output = ContentPipeline.execute_full_pipeline(raw)
        
        assert output is not None
        assert output.idea is not None
        assert len(output.hooks) > 0
        assert output.script is not None


class TestLearningFeedbackLoop:
    """Test feedback loop"""
    
    def test_process_performance(self):
        """Test performance analysis"""
        metrics = PostMetrics(
            views=5000,
            engagement=500,
            clicks=250,
            shares=100,
            comments=150
        )
        
        analysis = LearningFeedbackLoop.process_performance(
            metrics,
            "Test hook",
            "Test idea",
            viral_threshold=10
        )
        
        assert analysis.is_high_performer == True
        assert analysis.performance_tier in ["viral", "high", "medium", "low"]


class TestScoring:
    """Test scoring utilities"""
    
    def test_viral_score_calculation(self):
        """Test viral score calculation"""
        text = "I lost everything in 24 hours but here's what I learned"
        score = ScoringEngine.calculate_viral_score(text)
        
        assert 0 <= score <= 1
    
    def test_category_scoring(self):
        """Test category confidence scoring"""
        text = "I made a beat that slaps hard"
        scores = CategoryScorer.score_categories(text)
        
        assert "music" in scores
        assert scores["music"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
