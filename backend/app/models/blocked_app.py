"""
Blocked App Model
==================
Applications that are forbidden on lab PCs.
The system monitors running processes and can optionally auto-kill them.
"""

from datetime import datetime, timezone
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class BlockedApp(Base):
    __tablename__ = "blocked_apps"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Process name to watch for (e.g., "firefox", "steam", "vlc")
    app_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    # Optional: scope to a specific lab. NULL = blocked everywhere.
    lab_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("labs.id", ondelete="CASCADE"), nullable=True, index=True
    )

    # Whether to automatically kill the process when detected
    auto_kill: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        scope = f"lab_id={self.lab_id}" if self.lab_id else "global"
        return f"<BlockedApp(name='{self.app_name}', auto_kill={self.auto_kill}, {scope})>"
