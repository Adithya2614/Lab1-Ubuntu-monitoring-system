"""
Alert Schemas
==============
Pydantic v2 request/response models for alerts.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class AlertResponse(BaseModel):
    """Response body for a single alert."""
    id: int
    pc_id: Optional[int]
    pc_hostname: Optional[str] = None
    alert_type: str
    severity: str
    message: str
    resolved: bool
    resolved_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertListResponse(BaseModel):
    """Response body for listing alerts."""
    alerts: list[AlertResponse]
    total: int
    unresolved: int


class AlertResolveRequest(BaseModel):
    """Request body for resolving an alert."""
    resolved: bool = True
