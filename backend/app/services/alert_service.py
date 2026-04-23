"""
Alert Service
==============
Creates, queries, and resolves system alerts.
Handles heartbeat-based offline detection.
"""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.models.alert import Alert, AlertType, AlertSeverity
from backend.app.models.pc import PC


class AlertService:

    @staticmethod
    async def create_alert(db: AsyncSession, pc_id: Optional[int],
                           alert_type: str, message: str,
                           severity: str = AlertSeverity.INFO.value) -> Alert:
        alert = Alert(pc_id=pc_id, alert_type=alert_type,
                      message=message, severity=severity)
        db.add(alert)
        await db.flush()
        return alert

    @staticmethod
    async def get_alerts(db: AsyncSession, resolved: Optional[bool] = None,
                         alert_type: Optional[str] = None,
                         limit: int = 100) -> list[Alert]:
        stmt = select(Alert).options(selectinload(Alert.pc)).order_by(Alert.created_at.desc())
        if resolved is not None:
            stmt = stmt.where(Alert.resolved == resolved)
        if alert_type:
            stmt = stmt.where(Alert.alert_type == alert_type)
        stmt = stmt.limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def resolve_alert(db: AsyncSession, alert_id: int) -> Optional[Alert]:
        alert = await db.get(Alert, alert_id)
        if alert:
            alert.resolved = True
            alert.resolved_at = datetime.now(timezone.utc)
            await db.flush()
        return alert

    @staticmethod
    async def get_unresolved_count(db: AsyncSession) -> int:
        result = await db.scalar(
            select(func.count(Alert.id)).where(Alert.resolved == False))
        return result or 0
