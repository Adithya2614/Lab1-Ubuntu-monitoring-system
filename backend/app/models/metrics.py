"""
Metrics History Model
======================
Stores time-series metric snapshots for each PC.
Used for trend charts and reports.
"""

from datetime import datetime, timezone
from sqlalchemy import Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database import Base


class MetricsHistory(Base):
    __tablename__ = "metrics_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pc_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("pcs.id", ondelete="CASCADE"), nullable=False, index=True
    )

    cpu_load: Mapped[float] = mapped_column(Float, default=0.0)
    ram_used: Mapped[int] = mapped_column(Integer, default=0)       # MB
    ram_total: Mapped[int] = mapped_column(Integer, default=0)      # MB
    ram_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    disk_percentage: Mapped[float] = mapped_column(Float, default=0.0)

    # Network metrics (future use)
    network_rx: Mapped[int | None] = mapped_column(Integer, nullable=True)  # bytes/sec
    network_tx: Mapped[int | None] = mapped_column(Integer, nullable=True)  # bytes/sec

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # Relationship
    pc: Mapped["PC"] = relationship("PC", back_populates="metrics_history")  # noqa: F821

    def __repr__(self) -> str:
        return f"<MetricsHistory(pc_id={self.pc_id}, cpu={self.cpu_load}, ts={self.timestamp})>"
