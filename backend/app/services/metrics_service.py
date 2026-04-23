"""
Metrics Service
================
Stores metric snapshots in the database for time-series analytics.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.metrics import MetricsHistory
from backend.app.models.pc import PC


class MetricsService:

    @staticmethod
    async def store_snapshot(db: AsyncSession, pc_id: int,
                             cpu_load: float, ram_used: int, ram_total: int,
                             disk_percentage: float) -> MetricsHistory:
        """Store a single metric data point."""
        ram_pct = (ram_used / ram_total * 100) if ram_total > 0 else 0
        entry = MetricsHistory(
            pc_id=pc_id, cpu_load=cpu_load,
            ram_used=ram_used, ram_total=ram_total,
            ram_percentage=round(ram_pct, 1),
            disk_percentage=disk_percentage)
        db.add(entry)
        await db.flush()
        return entry

    @staticmethod
    async def get_history(db: AsyncSession, pc_id: int,
                          hours: int = 24) -> list[MetricsHistory]:
        """Get metric history for a PC within the last N hours."""
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        stmt = (select(MetricsHistory)
                .where(and_(MetricsHistory.pc_id == pc_id,
                            MetricsHistory.timestamp >= since))
                .order_by(MetricsHistory.timestamp.asc()))
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def cleanup_old(db: AsyncSession, days: int = 30) -> int:
        """Delete metric records older than N days."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = select(MetricsHistory).where(MetricsHistory.timestamp < cutoff)
        result = await db.execute(stmt)
        old = result.scalars().all()
        count = len(old)
        for record in old:
            await db.delete(record)
        await db.flush()
        return count
