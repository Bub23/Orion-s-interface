"""
Hooks routes
POST /hooks/generate - Generate hooks for idea
GET /hooks/status/{task_id} - Check hook generation status
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.api.deps import get_current_user_id
from app.workers.celery_app import celery_app

router = APIRouter(prefix="/hooks", tags=["hooks"])


class HookGenerateRequest(BaseModel):
    task_id: str  # Reference to completed pipeline task
    num_hooks: int = 8


class HookTaskResponse(BaseModel):
    task_id: str
    status: str
    message: str


class HookStatusResponse(BaseModel):
    task_id: str
    status: str
    hooks: list = None
    error: str = None


@router.post("/generate", response_model=HookTaskResponse)
async def generate_hooks(
    request: HookGenerateRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Generate hooks for an idea (from completed pipeline task)"""
    
    # Get original pipeline result
    pipeline_task = celery_app.AsyncResult(request.task_id)
    
    if pipeline_task.state != "SUCCESS":
        raise HTTPException(
            status_code=400,
            detail="Referenced pipeline task is not complete or failed"
        )
    
    # Hooks are already generated in pipeline, just return them
    result = pipeline_task.result
    
    return HookTaskResponse(
        task_id=request.task_id,
        status="complete",
        message=f"Hooks available from pipeline execution"
    )


@router.get("/status/{task_id}", response_model=HookStatusResponse)
async def get_hooks_status(
    task_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get hooks from completed pipeline"""
    
    task = celery_app.AsyncResult(task_id)
    
    if task.state == "SUCCESS":
        result = task.result
        hooks = result.get("hooks", [])
        return HookStatusResponse(
            task_id=task_id,
            status="success",
            hooks=hooks
        )
    elif task.state == "FAILURE":
        return HookStatusResponse(
            task_id=task_id,
            status="failed",
            error=str(task.info)
        )
    else:
        return HookStatusResponse(
            task_id=task_id,
            status=task.state.lower()
        )
