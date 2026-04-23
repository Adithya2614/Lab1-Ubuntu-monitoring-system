"""
Lab Model
==========
Represents a physical lab room (e.g., "Lab 1", "Physics Lab").
PCs belong to labs. Labs can have layout configurations.
"""

from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database import Base


class Lab(Base):
    __tablename__ = "labs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # JSON-stored layout configuration for drag-and-drop room designer
    # Structure: { "rows": 3, "cols": 4, "seats": [{"row": 0, "col": 0, "pc_id": 5}, ...] }
    layout: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    pcs: Mapped[list["PC"]] = relationship(  # noqa: F821
        "PC", back_populates="lab", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Lab(id={self.id}, name='{self.name}')>"
