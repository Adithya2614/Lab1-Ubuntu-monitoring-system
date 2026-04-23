"""
Metrics Router
===============
Metrics history and reporting endpoints.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.services.metrics_service import MetricsService
from backend.app.services.node_service import NodeService
from backend.app.schemas.metrics_schema import MetricsReceiveRequest


router = APIRouter(prefix="/api", tags=["metrics"])


@router.post("/metrics")
async def receive_metrics(data: MetricsReceiveRequest,
                          db: AsyncSession = Depends(get_db)):
    """Backward-compatible endpoint for receiving pushed metrics."""
    return {"status": "received"}


@router.get("/metrics/{pc_id}/history")
async def get_metrics_history(pc_id: int, hours: int = Query(24, le=720),
                              db: AsyncSession = Depends(get_db)):
    """Get time-series metric history for a PC."""
    pc = await NodeService.get_node_by_id(db, pc_id)
    if not pc:
        return {"error": "PC not found"}

    history = await MetricsService.get_history(db, pc_id, hours)
    return {
        "pc_id": pc_id, "pc_hostname": pc.hostname,
        "data_points": [{
            "cpu_load": h.cpu_load, "ram_used": h.ram_used,
            "ram_total": h.ram_total, "ram_percentage": h.ram_percentage,
            "disk_percentage": h.disk_percentage, "timestamp": h.timestamp,
        } for h in history],
    }
