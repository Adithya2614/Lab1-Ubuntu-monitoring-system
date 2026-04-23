"""
Audit Router
=============
Audit log retrieval. Backward-compatible with GET /api/audit.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.database import get_db
from backend.app.models.audit_log import AuditLog


router = APIRouter(prefix="/api", tags=["audit"])


@router.get("/audit")
async def get_audit_logs(
    limit: int = Query(100, le=500),
    action_type: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve audit logs. Backward-compatible with original format.
    Old format: {"logs": [{"timestamp": ..., "pc": ..., "removed": ...}]}
    New format adds more fields but preserves old ones.
    """
    stmt = (select(AuditLog)
            .options(selectinload(AuditLog.pc))
            .order_by(AuditLog.created_at.desc()))
    if action_type:
        stmt = stmt.where(AuditLog.action_type == action_type)
    stmt = stmt.limit(limit)

    result = await db.execute(stmt)
    logs = result.scalars().all()

    # Return in backward-compatible format
    formatted = []
    for log in logs:
        entry = {
            "id": log.id,
            "timestamp": log.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "pc": log.pc.hostname if log.pc else "system",
            "action_type": log.action_type,
            "message": log.message,
            "details": log.details,
            "performed_by": log.performed_by,
        }
        # Backward compat: if it's a package removal, add "removed" field
        if log.action_type == "remove_package" and log.details:
            entry["removed"] = log.details.get("removed_packages", "")
        formatted.append(entry)

    return {"logs": formatted}
