"""
PC Model
=========
Represents a monitored Linux PC / node.
Linked to a Lab via foreign key. Stores connection details and live status.
"""

from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum as SAEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database import Base
import enum


class PCStatus(str, enum.Enum):
    """Possible states of a monitored PC."""
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


class PC(Base):
    __tablename__ = "pcs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    hostname: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    ip: Mapped[str | None] = mapped_column(String(45), nullable=True)  # IPv4 or IPv6
    username: Mapped[str] = mapped_column(String(100), nullable=False)

    # Foreign key to the lab this PC belongs to (nullable = unassigned)
    lab_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("labs.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Status tracking
    status: Mapped[str] = mapped_column(
        String(20), default=PCStatus.UNKNOWN.value, nullable=False
    )
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Cached latest metrics snapshot (avoids constant DB queries)
    # Structure: {"cpu_load": "0.45", "ram_percentage": "67%", "disk_percentage": "42%"}
    cached_metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Vault manifest cache
    vault_manifest: Mapped[list | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    lab: Mapped["Lab | None"] = relationship("Lab", back_populates="pcs")  # noqa: F821
    metrics_history: Mapped[list["MetricsHistory"]] = relationship(  # noqa: F821
        "MetricsHistory", back_populates="pc", cascade="all, delete-orphan"
    )
    alerts: Mapped[list["Alert"]] = relationship(  # noqa: F821
        "Alert", back_populates="pc", cascade="all, delete-orphan"
    )
    actions: Mapped[list["Action"]] = relationship(  # noqa: F821
        "Action", back_populates="pc", cascade="all, delete-orphan"
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(  # noqa: F821
        "AuditLog", back_populates="pc", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<PC(id={self.id}, hostname='{self.hostname}', status='{self.status}')>"
