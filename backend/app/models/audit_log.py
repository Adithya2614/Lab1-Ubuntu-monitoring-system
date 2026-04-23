"""
Audit Log Model
================
Immutable record of all administrative actions for compliance.
Replaces the flat-file audit log with a queryable database table.
"""

from datetime import datetime, timezone
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Nullable: some actions are system-wide, not PC-specific
    pc_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("pcs.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # What was done (e.g., "remove_package", "bulk_import", "internet_disabled")
    action_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Human-readable summary
    message: Mapped[str] = mapped_column(Text, nullable=False)

    # Structured details (e.g., list of removed packages, CSV rows imported)
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Who performed the action (username or "system" for automated)
    performed_by: Mapped[str] = mapped_column(String(100), default="system", nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # Relationship
    pc: Mapped["PC | None"] = relationship("PC", back_populates="audit_logs")  # noqa: F821

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action='{self.action_type}', ts={self.created_at})>"
