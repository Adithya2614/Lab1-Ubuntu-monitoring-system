"""
Settings & Miscellaneous Schemas
=================================
Schemas for SSH keys, whitelist domains, blocked apps, and system settings.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


# --- SSH Key Schemas ---

class SSHKeyCreate(BaseModel):
    """Request body for generating a new SSH key pair."""
    name: str = Field(..., min_length=1, max_length=100, description="Key pair name")


class SSHKeyResponse(BaseModel):
    """Response body for an SSH key."""
    id: int
    name: str
    public_key: str
    fingerprint: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class SSHKeyDeployRequest(BaseModel):
    """Request body for deploying a key to target PCs."""
    key_id: int
    targets: list[str] = Field(..., min_length=1, description="PC hostnames")


class SSHKeyTestRequest(BaseModel):
    """Request body for testing SSH connectivity."""
    target: str = Field(..., description="PC hostname to test")


# --- Whitelist Domain Schemas ---

class WhitelistDomainCreate(BaseModel):
    """Request body for adding a domain to the whitelist."""
    domain: str = Field(..., min_length=1, max_length=500)
    lab_id: Optional[int] = None


class WhitelistDomainResponse(BaseModel):
    """Response body for a whitelisted domain."""
    id: int
    domain: str
    lab_id: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}


class WhitelistBulkImportRequest(BaseModel):
    """Request body for importing domains from CSV."""
    domains: list[str] = Field(..., min_length=1)
    lab_id: Optional[int] = None


# --- Blocked App Schemas ---

class BlockedAppCreate(BaseModel):
    """Request body for adding a blocked app."""
    app_name: str = Field(..., min_length=1, max_length=200)
    lab_id: Optional[int] = None
    auto_kill: bool = False


class BlockedAppResponse(BaseModel):
    """Response body for a blocked app."""
    id: int
    app_name: str
    lab_id: Optional[int]
    auto_kill: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class BlockedAppUpdate(BaseModel):
    """Request body for updating a blocked app."""
    app_name: Optional[str] = None
    auto_kill: Optional[bool] = None


# --- Audit Log Schemas ---

class AuditLogResponse(BaseModel):
    """Response body for an audit log entry."""
    id: int
    pc_id: Optional[int]
    pc_hostname: Optional[str] = None
    action_type: str
    message: str
    details: Optional[dict]
    performed_by: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    """
    Response body for listing audit logs.
    Backward-compatible with old {"logs": [...]} format.
    """
    logs: list[AuditLogResponse]
    total: int


# --- Report Schemas ---

class ReportOverview(BaseModel):
    """Overview statistics for the reports page."""
    total_pcs: int
    online_pcs: int
    offline_pcs: int
    total_labs: int
    total_alerts: int
    unresolved_alerts: int
    total_actions_today: int
    app_violations_today: int
    usb_events_today: int
