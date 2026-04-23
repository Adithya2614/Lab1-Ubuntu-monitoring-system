"""
SSH Key Model
==============
Manages SSH key pairs used for connecting to remote PCs.
Stores public key content; private key stays on filesystem.
"""

from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class SSHKey(Base):
    __tablename__ = "ssh_keys"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # The public key content (safe to store in DB)
    public_key: Mapped[str] = mapped_column(Text, nullable=False)

    # Path to the private key file on the controller machine
    # Never store private key content in DB
    private_key_path: Mapped[str] = mapped_column(String(500), nullable=False)

    # Optional fingerprint for display
    fingerprint: Mapped[str | None] = mapped_column(String(200), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<SSHKey(id={self.id}, name='{self.name}')>"
