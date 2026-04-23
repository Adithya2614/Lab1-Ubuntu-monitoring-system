"""
Alert Model
============
Stores system alerts: offline PCs, high resource usage,
unauthorized app detections, USB events, etc.
"""

from datetime import datetime, timezone
from sqlalchemy import Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database import Base
import enum


class AlertSeverity(str, enum.Enum):
    """Alert severity levels for UI display and filtering."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertType(str, enum.Enum):
    """Categories of alerts the system can generate."""
    PC_OFFLINE = "pc_offline"
    HIGH_CPU = "high_cpu"
    HIGH_RAM = "high_ram"
    HIGH_DISK = "high_disk"
    USB_INSERTED = "usb_inserted"
    USB_REMOVED = "usb_removed"
    UNAUTHORIZED_APP = "unauthorized_app"
    APP_KILLED = "app_killed"
    ACTION_FAILED = "action_failed"
    EXAM_MODE = "exam_mode"


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pc_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("pcs.id", ondelete="CASCADE"), nullable=True, index=True
    )

    alert_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(
        String(20), default=AlertSeverity.INFO.value, nullable=False
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)

    # Whether this alert has been acknowledged / resolved
    resolved: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # Relationship
    pc: Mapped["PC | None"] = relationship("PC", back_populates="alerts")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Alert(id={self.id}, type='{self.alert_type}', severity='{self.severity}')>"
