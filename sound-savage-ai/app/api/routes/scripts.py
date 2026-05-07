"""
Scripts routes
GET /scripts/status/{task_id} - Get script from pipeline
POST /scripts/render - Queue render job
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.api.deps import get_current_user_id
from app.workers.celery_app import celery_app
from app.workers.render_worker import render_video

router = APIRouter(prefix="/scripts", tags=["scripts"])


class ScriptStatusResponse(BaseModel):
    task_id: str
    status: str
    script: dict = None
    error: str = None


class RenderRequest(BaseModel):
    pipeline_task_id: str
    platform: str = "heygen"  # runway, heygen, synthesia
    style_template: str = None


class RenderTaskResponse(BaseModel):
    render_task_id: str
    status: str
    message: str


@router.get("/status/{task_id}", response_model=ScriptStatusResponse)
async def get_script_status(
    task_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get script from completed pipeline"""
    
    task = celery_app.AsyncResult(task_id)
    
    if task.state == "SUCCESS":
        result = task.result
        script = result.get("script", {})
        return ScriptStatusResponse(
            task_id=task_id,
            status="success",
            script=script
        )
    elif task.state == "FAILURE":
        return ScriptStatusResponse(
            task_id=task_id,
            status="failed",
            error=str(task.info)
        )
    else:
        return ScriptStatusResponse(
            task_id=task_id,
            status=task.state.lower()
        )


@router.post("/render", response_model=RenderTaskResponse)
async def queue_render(
    request: RenderRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Queue render job for script"""
    
    # Verify pipeline task exists and completed
    pipeline_task = celery_app.AsyncResult(request.pipeline_task_id)
    
    if pipeline_task.state != "SUCCESS":
        raise HTTPException(
            status_code=400,
            detail="Referenced pipeline task is not complete"
        )
    
    # Queue render task
    render_task = render_video.apply_async(
        args=[
            request.pipeline_task_id,
            request.platform,
            request.style_template
        ],
        queue="render"
    )
    
    return RenderTaskResponse(
        render_task_id=render_task.id,
        status="queued",
        message=f"Render queued on {request.platform}. Check /render/status/{render_task.id}"
    )
