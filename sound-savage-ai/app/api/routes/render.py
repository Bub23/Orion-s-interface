"""
Render routes
GET /render/status/{task_id} - Check render status
POST /render/complete - Handle completed render
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.api.deps import get_current_user_id
from app.workers.celery_app import celery_app
from app.workers.render_worker import handle_render_complete

router = APIRouter(prefix="/render", tags=["render"])


class RenderStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: int = None
    output_url: str = None
    error: str = None


class RenderCompleteRequest(BaseModel):
    render_task_id: str
    output_url: str
    render_duration: int


class RenderCompleteResponse(BaseModel):
    task_id: str
    status: str
    message: str


@router.get("/status/{task_id}", response_model=RenderStatusResponse)
async def get_render_status(
    task_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Check render job status"""
    
    task = celery_app.AsyncResult(task_id)
    
    if task.state == "PROCESSING":
        meta = task.info if isinstance(task.info, dict) else {}
        return RenderStatusResponse(
            task_id=task_id,
            status="processing",
            progress=meta.get("progress", 0)
        )
    elif task.state == "SUCCESS":
        result = task.result
        return RenderStatusResponse(
            task_id=task_id,
            status="complete",
            output_url=result.get("output_url")
        )
    elif task.state == "FAILURE":
        return RenderStatusResponse(
            task_id=task_id,
            status="failed",
            error=str(task.info)
        )
    else:
        return RenderStatusResponse(
            task_id=task_id,
            status=task.state.lower()
        )


@router.post("/complete", response_model=RenderCompleteResponse)
async def notify_render_complete(
    request: RenderCompleteRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Webhook: Notify when external render completes"""
    
    # Queue handler task
    handler_task = handle_render_complete.apply_async(
        args=[
            request.render_task_id,
            request.output_url,
            request.render_duration
        ],
        queue="analytics"
    )
    
    return RenderCompleteResponse(
        task_id=handler_task.id,
        status="queued",
        message="Render completion being processed"
    )
