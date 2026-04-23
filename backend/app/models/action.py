"""
Action Model
==============
Tracks the lifecycle of executed actions (single or bulk).
Each row represents one action on one PC, enabling per-node
progress tracking, retry, and history.
"""

from datetime import datetime, timezone
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database import Base
import enum


class ActionStatus(str, enum.Enum):
    """Lifecycle states for an action execution."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class Action(Base):
    __tablename__ = "actions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    pc_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("pcs.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Batch identifier — actions triggered together share the same batch_id
    batch_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)

    # The action being performed (e.g., "collect_metrics", "install_package")
    action_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Current lifecycle state
    status: Mapped[str] = mapped_column(
        String(20), default=ActionStatus.PENDING.value, nullable=False, index=True
    )

    # Action parameters sent (e.g., {"package_name": "vim"})
    parameters: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Result data on completion (stdout, parsed data, error message)
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Error message on failure
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationship
    pc: Mapped["PC | None"] = relationship("PC", back_populates="actions")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Action(id={self.id}, type='{self.action_type}', status='{self.status}')>"
