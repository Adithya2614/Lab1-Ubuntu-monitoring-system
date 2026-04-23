"""
Node Service
==============
Business logic for PC/node management: CRUD, bulk import,
CSV parsing, IP range scanning, and duplicate detection.
"""

import csv
import io
import re
from typing import Optional
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.models.pc import PC, PCStatus
from backend.app.models.lab import Lab
from backend.app.services.ansible_service import AnsibleService


class NodeService:
    """Handles all PC/node CRUD and bulk import operations."""

    @staticmethod
    async def get_all_nodes(db: AsyncSession) -> list[dict]:
        """Get all PCs with lab info, backward-compatible format."""
        stmt = select(PC).options(selectinload(PC.lab)).order_by(PC.hostname)
        result = await db.execute(stmt)
        pcs = result.scalars().all()
        nodes = []
        for pc in pcs:
            nodes.append({
                "id": pc.id, "hostname": pc.hostname, "name": pc.hostname,
                "ip": pc.ip, "username": pc.username, "lab_id": pc.lab_id,
                "lab_name": pc.lab.name if pc.lab else None,
                "status": pc.status, "last_seen": pc.last_seen,
                "facts": pc.cached_metrics, "vault_manifest": pc.vault_manifest or [],
                "created_at": pc.created_at,
            })
        return nodes

    @staticmethod
    async def get_node_by_hostname(db: AsyncSession, hostname: str) -> Optional[PC]:
        stmt = select(PC).where(PC.hostname == hostname)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_node_by_id(db: AsyncSession, pc_id: int) -> Optional[PC]:
        stmt = select(PC).options(selectinload(PC.lab)).where(PC.id == pc_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_node(db: AsyncSession, hostname: str, username: str,
                          password: str, ip: Optional[str] = None,
                          lab_id: Optional[int] = None) -> PC:
        if not hostname.endswith(".local") and "." not in hostname:
            hostname += ".local"
        group = "ubuntu_nodes"
        if lab_id:
            lab = await db.get(Lab, lab_id)
            if lab:
                group = re.sub(r"[^a-zA-Z0-9_]", "_", lab.name.lower())
        await AnsibleService.add_host_to_inventory(
            hostname=hostname, username=username, password=password, ip=ip, group=group)
        pc = PC(hostname=hostname, ip=ip, username=username,
                lab_id=lab_id, status=PCStatus.UNKNOWN.value)
        db.add(pc)
        await db.flush()
        return pc

    @staticmethod
    async def delete_node(db: AsyncSession, pc: PC) -> bool:
        await AnsibleService.remove_host_from_inventory(pc.hostname)
        await db.delete(pc)
        await db.flush()
        return True

    @staticmethod
    async def update_node_status(db: AsyncSession, hostname: str, status: str,
                                  metrics: Optional[dict] = None) -> Optional[PC]:
        pc = await NodeService.get_node_by_hostname(db, hostname)
        if not pc:
            return None
        pc.status = status
        if status == PCStatus.ONLINE.value:
            pc.last_seen = datetime.now(timezone.utc)
        if metrics is not None:
            pc.cached_metrics = metrics
        await db.flush()
        return pc

    @staticmethod
    def parse_csv(csv_text: str) -> tuple[list[dict], list[dict]]:
        valid, invalid = [], []
        reader = csv.DictReader(io.StringIO(csv_text))
        for i, row in enumerate(reader):
            hostname = row.get("hostname", "").strip()
            username = row.get("username", "").strip()
            if not hostname or not username:
                invalid.append({"row": i+2, "data": row, "error": "Missing hostname/username"})
                continue
            if not re.match(r"^[a-zA-Z0-9._-]+$", hostname):
                invalid.append({"row": i+2, "data": row, "error": f"Invalid hostname: {hostname}"})
                continue
            valid.append({"hostname": hostname, "ip": row.get("ip","").strip() or None,
                          "username": username, "lab": row.get("lab","").strip() or None})
        return valid, invalid

    @staticmethod
    def expand_ip_range(ip_range: str) -> list[str]:
        ips = []
        try:
            parts = ip_range.split("-")
            base, end = parts[0].strip(), parts[1].strip()
            prefix = ".".join(base.split(".")[:-1])
            start_num = int(base.split(".")[-1])
            end_num = int(end) if "." not in end else int(end.split(".")[-1])
            for i in range(start_num, end_num + 1):
                ips.append(f"{prefix}.{i}")
        except Exception:
            pass
        return ips

    @staticmethod
    async def check_duplicates(db: AsyncSession, hostnames: list[str]) -> list[str]:
        stmt = select(PC.hostname).where(PC.hostname.in_(hostnames))
        result = await db.execute(stmt)
        return [row[0] for row in result.fetchall()]

    @staticmethod
    async def bulk_create_nodes(db: AsyncSession, entries: list[dict],
                                 default_password: str,
                                 default_lab_id: Optional[int] = None) -> dict:
        created, skipped, failed, errors = 0, 0, 0, []
        for entry in entries:
            try:
                existing = await NodeService.get_node_by_hostname(db, entry["hostname"])
                if existing:
                    skipped += 1
                    continue
                lab_id = default_lab_id
                if entry.get("lab"):
                    lab_result = await db.execute(select(Lab).where(Lab.name == entry["lab"]))
                    lab = lab_result.scalar_one_or_none()
                    if lab:
                        lab_id = lab.id
                await NodeService.create_node(
                    db=db, hostname=entry["hostname"],
                    username=entry.get("username", "student"),
                    password=entry.get("password", default_password),
                    ip=entry.get("ip"), lab_id=lab_id)
                created += 1
            except Exception as e:
                failed += 1
                errors.append({"hostname": entry.get("hostname"), "error": str(e)})
        return {"created": created, "skipped": skipped, "failed": failed, "errors": errors}

    @staticmethod
    async def get_stats(db: AsyncSession) -> dict:
        total = await db.scalar(select(func.count(PC.id)))
        online = await db.scalar(
            select(func.count(PC.id)).where(PC.status == PCStatus.ONLINE.value))
        return {"total": total or 0, "online": online or 0,
                "offline": (total or 0) - (online or 0)}
