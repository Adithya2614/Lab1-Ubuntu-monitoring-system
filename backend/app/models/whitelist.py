"""
Whitelist Domain Model
=======================
Domains that are allowed when website restriction is active.
Can be global or scoped to a specific lab.
"""

from datetime import datetime, timezone
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class WhitelistDomain(Base):
    __tablename__ = "whitelist_domains"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # The domain to whitelist (e.g., "google.com", "examportal.edu")
    domain: Mapped[str] = mapped_column(String(500), nullable=False, index=True)

    # Optional: scope to a specific lab. NULL = global whitelist.
    lab_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("labs.id", ondelete="CASCADE"), nullable=True, index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        scope = f"lab_id={self.lab_id}" if self.lab_id else "global"
        return f"<WhitelistDomain(domain='{self.domain}', {scope})>"
