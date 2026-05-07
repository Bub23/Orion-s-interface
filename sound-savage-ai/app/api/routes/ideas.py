"""
Ideas routes
POST /ideas/create - Submit idea and queue pipeline
GET /ideas/status/{task_id} - Check pipeline status
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.api.deps import get_current_user_id
from app.workers.content_pipeline_worker import generate_content_pipeline

router = APIRouter(prefix="/ideas", tags=["ideas"])


class IdeaSubmitRequest(BaseModel):
    raw_input: str
    source: str = "manual"


class IdeaTaskResponse(BaseModel):
    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: dict = None
    current: int = None
    total: int = None


@router.post("/create", response_model=IdeaTaskResponse)
async def create_idea(
    request: IdeaSubmitRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Submit idea and queue content pipeline"""
    
    # Queue async pipeline task
    task = generate_content_pipeline.apply_async(
        args=[user_id, request.raw_input, request.source],
        queue="content_pipeline"
    )
    
    return IdeaTaskResponse(
        task_id=task.id,
        status="queued",
        message="Content pipeline queued. Check /ideas/status/{task_id} for progress."
    )


@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_pipeline_status(task_id: str):
    """Check content pipeline status"""
    
    task = generate_content_pipeline.AsyncResult(task_id)
    
    if task.state == "PENDING":
        return TaskStatusResponse(
            task_id=task_id,
            status="pending",
            result={"message": "Task not found"}
        )
    elif task.state == "PROCESSING":
        meta = task.info if isinstance(task.info, dict) else {}
        return TaskStatusResponse(
            task_id=task_id,
            status="processing",
            current=meta.get("current", 0),
            total=meta.get("total", 0)
        )
    elif task.state == "SUCCESS":
        return TaskStatusResponse(
            task_id=task_id,
            status="success",
            result=task.result
        )
    elif task.state == "FAILURE":
        return TaskStatusResponse(
            task_id=task_id,
            status="failed",
            result={"error": str(task.info)}
        )
    else:
        return TaskStatusResponse(
            task_id=task_id,
            status=task.state.lower()
        )
