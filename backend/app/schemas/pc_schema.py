"""
PC Schemas
===========
Pydantic v2 request/response models for PC management,
including single add, bulk add (CSV, IP range, paste), and responses.
"""

from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


class PCCreate(BaseModel):
    """Request body for adding a single PC (backward-compatible with AddNodeRequest)."""
    hostname: str = Field(..., min_length=1, max_length=200)
    ip: Optional[str] = Field(None, max_length=45)
    user: str = Field(..., alias="username", min_length=1, max_length=100)
    password: str = Field(..., min_length=1)
    lab_id: Optional[int] = None

    # Allow both 'user' and 'username' for backward compatibility
    model_config = {"populate_by_name": True}

    @field_validator("ip")
    @classmethod
    def validate_ip(cls, v):
        if v and not re.match(r"^[\d.]+$|^[\da-fA-F:]+$", v):
            raise ValueError("Invalid IP address format")
        return v

    @field_validator("hostname")
    @classmethod
    def validate_hostname(cls, v):
        # Allow hostnames with dots, hyphens, and alphanumeric chars
        if not re.match(r"^[a-zA-Z0-9._-]+$", v):
            raise ValueError("Hostname contains invalid characters")
        return v


class PCBulkCSVRow(BaseModel):
    """A single row from CSV import."""
    hostname: str
    ip: Optional[str] = None
    username: str
    lab: Optional[str] = None  # Lab name (will be resolved to lab_id)


class PCBulkAddRequest(BaseModel):
    """Request body for bulk adding PCs."""
    method: str = Field(..., pattern="^(csv|paste|ip_range|auto_discover)$")

    # For CSV / paste methods: list of PC entries
    pcs: Optional[list[PCBulkCSVRow]] = None

    # For IP range method: e.g., "192.168.1.10-50"
    ip_range: Optional[str] = None
    default_username: Optional[str] = None
    default_password: Optional[str] = None
    default_lab_id: Optional[int] = None

    # For auto-discover: network prefix
    network_prefix: Optional[str] = None


class PCBulkPreviewResponse(BaseModel):
    """Response for previewing bulk import (before actually importing)."""
    valid: list[PCBulkCSVRow]
    duplicates: list[str]  # Hostnames that already exist
    invalid: list[dict]    # Rows with validation errors
    total: int


class PCResponse(BaseModel):
    """Response body for a single PC — backward-compatible with old /api/nodes format."""
    id: int
    hostname: str
    name: str  # Alias for hostname (backward compat: old frontend uses node.name)
    ip: Optional[str]
    username: str
    lab_id: Optional[int]
    lab_name: Optional[str] = None
    status: str
    last_seen: Optional[datetime]
    facts: Optional[dict] = None      # Backward compat: cached_metrics mapped to "facts"
    vault_manifest: Optional[list] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PCListResponse(BaseModel):
    """Response for listing PCs — backward-compatible with {"nodes": [...]}."""
    nodes: list[PCResponse]
    total: int = 0
    online: int = 0
    offline: int = 0


class PCUpdate(BaseModel):
    """Request body for updating a PC."""
    hostname: Optional[str] = None
    ip: Optional[str] = None
    username: Optional[str] = None
    lab_id: Optional[int] = None


class PCAssignLabRequest(BaseModel):
    """Request body for assigning PCs to a lab."""
    pc_ids: list[int]
    lab_id: Optional[int] = None  # None = unassign from lab
