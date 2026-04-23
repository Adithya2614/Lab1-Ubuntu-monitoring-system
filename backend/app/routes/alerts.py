"""
Alerts Router
==============
Alert management and retrieval endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from backend.app.database import get_db
from backend.app.services.alert_service import AlertService


router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("")
async def list_alerts(
    resolved: Optional[bool] = Query(None),
    alert_type: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db),
):
    alerts = await AlertService.get_alerts(db, resolved, alert_type, limit)
    unresolved = await AlertService.get_unresolved_count(db)
    return {
        "alerts": [{
            "id": a.id, "pc_id": a.pc_id,
            "pc_hostname": a.pc.hostname if a.pc else None,
            "alert_type": a.alert_type, "severity": a.severity,
            "message": a.message, "resolved": a.resolved,
            "resolved_at": a.resolved_at, "created_at": a.created_at,
        } for a in alerts],
        "total": len(alerts),
        "unresolved": unresolved,
    }


@router.post("/{alert_id}/resolve")
async def resolve_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    alert = await AlertService.resolve_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"status": "success", "id": alert.id}
