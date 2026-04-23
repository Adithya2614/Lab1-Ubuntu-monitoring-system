"""
WMI ORM Models Package
=======================
All SQLAlchemy ORM models are imported here so that
Base.metadata knows about every table when init_db() is called.
"""

from backend.app.models.lab import Lab
from backend.app.models.pc import PC
from backend.app.models.metrics import MetricsHistory
from backend.app.models.alert import Alert
from backend.app.models.audit_log import AuditLog
from backend.app.models.ssh_key import SSHKey
from backend.app.models.action import Action
from backend.app.models.whitelist import WhitelistDomain
from backend.app.models.blocked_app import BlockedApp

__all__ = [
    "Lab",
    "PC",
    "MetricsHistory",
    "Alert",
    "AuditLog",
    "SSHKey",
    "Action",
    "WhitelistDomain",
    "BlockedApp",
]
