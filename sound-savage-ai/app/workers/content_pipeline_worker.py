"""
Content pipeline worker
Orchestrates full idea → hook → script generation
Runs asynchronously in background
"""

from app.workers.celery_app import celery_app
from app.services.pipeline import ContentPipeline
from sqlalchemy.ext.asyncio import AsyncSession
import json


@celery_app.task(bind=True, name="tasks.generate_content_pipeline")
def generate_content_pipeline(
    self,
    user_id: str,
    raw_input: str,
    source: str = "manual"
):
    """
    Generate full content (idea → hooks → scripts)
    
    Args:
        user_id: User ID for DB persistence
        raw_input: Raw idea text
        source: "manual", "trend", or "remix"
    
    Returns:
        Pipeline output with idea, hooks, script
    """
    
    try:
        # Update task status
        self.update_state(state='PROCESSING', meta={'current': 1, 'total': 3})
        
        # Execute pipeline
        output = ContentPipeline.execute_full_pipeline(
            raw_input=raw_input,
            source=source,
            num_hooks=8
        )
        
        if not output:
            return {
                "status": "failed",
                "error": "Idea validation failed",
                "user_id": user_id
            }
        
        # Update status
        self.update_state(state='PROCESSING', meta={'current': 2, 'total': 3})
        
        # Convert to serializable format
        result = {
            "status": "success",
            "user_id": user_id,
            "idea": {
                "raw_input": output.idea.raw_input,
                "source": output.idea.source,
                "category": output.idea.category,
                "viral_score": output.idea.viral_score,
                "word_count": output.idea.word_count,
            },
            "hooks": [
                {
                    "text": hook.text,
                    "hook_type": hook.hook_type,
                    "intensity": hook.intensity,
                    "variants": hook.variants
                }
                for hook in output.hooks
            ],
            "script": {
                "hook": output.script.hook,
                "pacing": output.script.pacing,
                "total_duration": output.script.total_duration,
                "cta": output.script.cta,
                "sections": [
                    {
                        "title": s.title,
                        "duration_seconds": s.duration_seconds,
                        "content": s.content
                    }
                    for s in output.script.sections
                ]
            }
        }
        
        # Final status
        self.update_state(state='SUCCESS', meta={'current': 3, 'total': 3})
        
        return result
        
    except Exception as e:
        self.update_state(
            state='FAILURE',
            meta={
                'exc_type': type(e).__name__,
                'exc_message': str(e)
            }
        )
        return {
            "status": "failed",
            "error": str(e),
            "user_id": user_id
        }


@celery_app.task(name="tasks.batch_generate_content")
def batch_generate_content(user_id: str, ideas: list):
    """
    Generate content for multiple ideas
    
    Args:
        user_id: User ID
        ideas: List of idea strings
    
    Returns:
        List of pipeline outputs
    """
    results = []
    
    for idea in ideas:
        task = generate_content_pipeline.apply_async(
            args=[user_id, idea, "manual"]
        )
        results.append({
            "idea": idea,
            "task_id": task.id
        })
    
    return results
