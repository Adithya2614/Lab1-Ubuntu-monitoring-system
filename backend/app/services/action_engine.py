"""
Action Engine
==============
Parallel action execution engine using asyncio.
Replaces sequential execution with concurrent worker pool.
Tracks per-node progress and supports retry.
"""

import asyncio
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.models.action import Action, ActionStatus
from backend.app.models.pc import PC
from backend.app.services.ansible_service import AnsibleService


# Maximum concurrent Ansible playbook executions
MAX_CONCURRENT = 10


class ActionEngine:
    """Manages parallel action execution across multiple PCs."""

    @staticmethod
    async def execute_single(
        db: AsyncSession,
        target: str,
        action_type: str,
        parameters: Optional[dict] = None,
    ) -> dict:
        """
        Execute a single action on one target.
        Preserves full backward compatibility with the old /api/action endpoint.
        """
        # Map action_type to playbook (preserved from original router.py)
        playbook_map = {
            "ping": "ping.yml",
            "collect_metrics": "collect_metrics.yml",
            "install_package": "manage_packages.yml",
            "remove_package": "manage_packages.yml",
            "update_internet": "manage_internet.yml",
            "list_files": "list_files.yml",
            "delete_files": "delete_files.yml",
            "list_packages": "get_packages.yml",
            "manage_browsers": "manage_browsers.yml",
            "archive_files": "archive_files.yml",
            "restore_files": "restore_files.yml",
            "get_vault": "get_vault.yml",
            "cleanup_apps": "cleanup_apps.yml",
            "generate_app_whitelist": "generate_app_whitelist.yml",
            "sync_time": "sync_time.yml",
            "restrict_websites": "restrict_websites.yml",
            # New playbooks
            "detect_usb": "detect_usb.yml",
            "check_blocked_apps": "check_blocked_apps.yml",
            "kill_process": "kill_process.yml",
            "setup_dns_whitelist": "setup_dns_whitelist.yml",
            "clear_dns_whitelist": "clear_dns_whitelist.yml",
            "deploy_ssh_key": "deploy_ssh_key.yml",
            "remove_ssh_key": "remove_ssh_key.yml",
            "scan_network": "scan_network.yml",
        }

        playbook = playbook_map.get(action_type)
        if not playbook:
            return {"status": "error", "message": f"Unknown action type: {action_type}"}

        # Inject action-specific defaults (preserved from original)
        params = (parameters or {}).copy()
        if action_type == "remove_package":
            params["state"] = "absent"
        elif action_type == "install_package":
            params["state"] = "present"
        if action_type == "manage_browsers" and "action" in params:
            params["browser_action"] = params.pop("action")

        result = await AnsibleService.run_playbook(playbook, target, params)

        # Post-process results (preserved from original router.py)
        if result.get("status") == "success" and "data" in result:
            data = result["data"]

            if action_type == "collect_metrics":
                metrics = AnsibleService.parse_metrics_from_playbook(data, target)
                if metrics:
                    # Update PC in DB
                    pc = await db.execute(select(PC).where(PC.hostname == target))
                    pc_obj = pc.scalar_one_or_none()
                    if pc_obj:
                        pc_obj.status = "online"
                        pc_obj.last_seen = datetime.now(timezone.utc)
                        pc_obj.cached_metrics = {
                            "cpu_load": metrics["cpu_load"],
                            "ram_percentage": metrics["ram_percentage"],
                            "disk_percentage": metrics["disk_percentage"],
                        }

            elif action_type == "list_files":
                parsed = AnsibleService.parse_files_from_playbook(data, target)
                if parsed is not None:
                    result["data"] = parsed

            elif action_type == "list_packages":
                parsed = AnsibleService.parse_packages_from_playbook(data, target)
                if parsed is not None:
                    result["data"] = parsed

            elif action_type in ("archive_files", "get_vault"):
                manifest = AnsibleService.parse_vault_from_playbook(data, target)
                if manifest is not None:
                    pc = await db.execute(select(PC).where(PC.hostname == target))
                    pc_obj = pc.scalar_one_or_none()
                    if pc_obj:
                        pc_obj.vault_manifest = manifest
                    result["data"] = manifest

            elif action_type == "restore_files":
                pc = await db.execute(select(PC).where(PC.hostname == target))
                pc_obj = pc.scalar_one_or_none()
                if pc_obj:
                    pc_obj.vault_manifest = []

            elif action_type == "cleanup_apps":
                parsed = AnsibleService.parse_cleanup_from_playbook(data, target)
                if parsed is not None:
                    result["data"] = parsed

        return result

    @staticmethod
    async def execute_bulk(
        db: AsyncSession,
        targets: list[str],
        action_type: str,
        parameters: Optional[dict] = None,
    ) -> dict:
        """
        Execute an action across multiple PCs in parallel.
        Uses a semaphore to limit concurrency.
        Returns batch status with per-node results.
        """
        batch_id = str(uuid.uuid4())[:8]
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        results = {}

        async def run_one(target: str):
            async with semaphore:
                try:
                    result = await ActionEngine.execute_single(
                        db, target, action_type, parameters)
                    results[target] = {
                        "status": result.get("status", "error"),
                        "data": result.get("data"),
                        "message": result.get("message"),
                    }
                except Exception as e:
                    results[target] = {"status": "failed", "message": str(e)}

        # Run all targets concurrently (bounded by semaphore)
        tasks = [run_one(t) for t in targets]
        await asyncio.gather(*tasks)

        success = sum(1 for r in results.values() if r["status"] == "success")
        failed = sum(1 for r in results.values() if r["status"] != "success")

        return {
            "batch_id": batch_id,
            "action_type": action_type,
            "total": len(targets),
            "success": success,
            "failed": failed,
            "results": results,
        }
