"""
Render router service
- Select appropriate rendering API
- Route jobs to workers
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.content import Script, RenderJob
from uuid import uuid4


class RenderRouter:
    """Routes scripts to appropriate rendering platform"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def route_render_job(
        self,
        script_id: str,
        style_template: str = None
    ) -> RenderJob:
        """Create render job with platform selection"""
        
        # Get script
        result = await self.db.execute(
            select(Script).where(Script.id == script_id)
        )
        script = result.scalar_one()
        
        # Select renderer
        platform = self._select_renderer(script)
        
        # Create job
        render_job = RenderJob(
            id=str(uuid4()),
            script_id=script_id,
            platform=platform,
            style_template=style_template,
            status="queued"
        )
        
        self.db.add(render_job)
        script.status = "rendering"
        self.db.add(script)
        await self.db.commit()
        await self.db.refresh(render_job)
        
        return render_job
    
    def _select_renderer(self, script: Script) -> str:
        """
        Select rendering platform based on script characteristics
        
        Runway → cinematic, visual storytelling
        HeyGen → talking head, presenter style
        Synthesia → structured, educational, corporate
        """
        
        body_text = " ".join(script.body) if isinstance(script.body, list) else str(script.body)
        
        # Heuristics for platform selection
        if any(word in body_text.lower() for word in ["visual", "scene", "cinematic", "show"]):
            return "runway"
        elif any(word in body_text.lower() for word in ["explain", "explain", "teach", "learn"]):
            return "synthesia"
        else:
            return "heygen"
