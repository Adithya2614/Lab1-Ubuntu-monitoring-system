"""
Action Schemas
===============
Pydantic v2 request/response models for action execution.
Backward-compatible with the original ActionRequest.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class ActionRequest(BaseModel):
    """
    Request body for executing a single action.
    Backward-compatible with the original controller/api/models.py ActionRequest.
    """
    target: str = Field(..., description="Hostname of the target PC")
    action_type: str = Field(..., description="Action to execute (e.g., 'collect_metrics')")
    parameters: Optional[dict] = Field(default_factory=dict)


class BulkActionRequest(BaseModel):
    """Request body for executing an action across multiple PCs in parallel."""
    targets: list[str] = Field(..., min_length=1, description="List of PC hostnames")
    action_type: str = Field(..., description="Action to execute on all targets")
    parameters: Optional[dict] = Field(default_factory=dict)


class ActionStatusResponse(BaseModel):
    """Response body for a single action's status."""
    id: int
    pc_hostname: Optional[str]
    action_type: str
    status: str
    parameters: Optional[dict]
    result: Optional[dict]
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}


class BulkActionStatusResponse(BaseModel):
    """Response body for bulk action progress."""
    batch_id: str
    action_type: str
    total: int
    pending: int
    running: int
    success: int
    failed: int
    actions: list[ActionStatusResponse]


class ActionResultResponse(BaseModel):
    """
    Backward-compatible response for POST /api/action.
    Matches the old format: {"status": "success", "data": {...}}
    """
    status: str
    data: Optional[dict | list] = None
    message: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
