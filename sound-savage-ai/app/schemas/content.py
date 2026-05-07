"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ─────────────────────────────────────────
# AUTH SCHEMAS
# ─────────────────────────────────────────

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ─────────────────────────────────────────
# CONTENT SCHEMAS
# ─────────────────────────────────────────

class ContentIdeaCreate(BaseModel):
    raw_input: str
    category: str  # music, story, ai, brand
    source: str = "manual"  # manual, trend, remix


class ContentIdeaResponse(BaseModel):
    id: str
    source: str
    raw_input: str
    category: str
    viral_score: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─────────────────────────────────────────
# HOOK SCHEMAS
# ─────────────────────────────────────────

class HookGenerateRequest(BaseModel):
    content_id: str
    num_hooks: int = 5


class HookResponse(BaseModel):
    id: str
    hook_text: str
    hook_type: str
    performance_score: float
    is_high_performer: bool

    class Config:
        from_attributes = True


# ─────────────────────────────────────────
# SCRIPT SCHEMAS
# ─────────────────────────────────────────

class ScriptGenerateRequest(BaseModel):
    hook_id: str
    pacing: str = "medium"  # fast, medium, slow


class ScriptResponse(BaseModel):
    id: str
    hook: str
    body: list
    cta: str
    pacing: str
    status: str

    class Config:
        from_attributes = True


# ─────────────────────────────────────────
# RENDER SCHEMAS
# ─────────────────────────────────────────

class RenderCreateRequest(BaseModel):
    script_id: str
    platform: str  # runway, heygen, synthesia
    style_template: Optional[str] = None


class RenderJobResponse(BaseModel):
    id: str
    script_id: str
    platform: str
    status: str
    output_url: Optional[str] = None

    class Config:
        from_attributes = True
