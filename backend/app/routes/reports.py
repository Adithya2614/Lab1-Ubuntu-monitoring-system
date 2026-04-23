"""
Reports Router — analytics data for charts.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone, timedelta

from backend.app.database import get_db
from backend.app.models.pc import PC, PCStatus
from backend.app.models.lab import Lab
from backend.app.models.alert import Alert
from backend.app.models.audit_log import AuditLog
from backend.app.services.metrics_service import MetricsService
from backend.app.services.node_service import NodeService

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/overview")
async def get_overview(db: AsyncSession = Depends(get_db)):
    """Summary statistics for the reports page."""
    stats = await NodeService.get_stats(db)
    total_labs = await db.scalar(select(func.count(Lab.id)))
    total_alerts = await db.scalar(select(func.count(Alert.id)))
    unresolved = await db.scalar(
        select(func.count(Alert.id)).where(Alert.resolved == False))

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)
    actions_today = await db.scalar(
        select(func.count(AuditLog.id)).where(AuditLog.created_at >= today_start))

    return {
        "total_pcs": stats["total"], "online_pcs": stats["online"],
        "offline_pcs": stats["offline"], "total_labs": total_labs or 0,
        "total_alerts": total_alerts or 0, "unresolved_alerts": unresolved or 0,
        "total_actions_today": actions_today or 0,
    }


@router.get("/metrics/{pc_id}")
async def get_pc_metrics(pc_id: int, hours: int = Query(24, le=720),
                         db: AsyncSession = Depends(get_db)):
    """Time-series metrics for charts."""
    history = await MetricsService.get_history(db, pc_id, hours)
    return {
        "data_points": [{
            "cpu_load": h.cpu_load, "ram_percentage": h.ram_percentage,
            "disk_percentage": h.disk_percentage,
            "timestamp": h.timestamp.isoformat(),
        } for h in history]
    }
