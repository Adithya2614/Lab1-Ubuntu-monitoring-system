"""
Lab Schemas
============
Pydantic v2 request/response models for Lab CRUD operations.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class LabCreate(BaseModel):
    """Request body for creating a new lab."""
    name: str = Field(..., min_length=1, max_length=100, description="Lab display name")
    description: Optional[str] = Field(None, max_length=500, description="Lab description")


class LabUpdate(BaseModel):
    """Request body for updating a lab."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    layout: Optional[dict] = Field(None, description="Room layout config (JSON)")


class LabResponse(BaseModel):
    """Response body for a lab."""
    id: int
    name: str
    description: Optional[str]
    layout: Optional[dict]
    pc_count: int = 0
    online_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class LabListResponse(BaseModel):
    """Response body for listing all labs."""
    labs: list[LabResponse]
    total: int
