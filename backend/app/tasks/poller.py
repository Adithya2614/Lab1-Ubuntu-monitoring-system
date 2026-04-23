"""
Background Poller
==================
Replaces the original threading-based poller with asyncio.
Hybrid model: periodic heartbeat + instant status change push.
"""

import asyncio
from datetime import datetime, timezone

from backend.app.config import get_settings
from backend.app.database import async_session_factory
from backend.app.services.ansible_service import AnsibleService
from backend.app.services.node_service import NodeService
from backend.app.services.metrics_service import MetricsService
from backend.app.services.alert_service import AlertService
from backend.app.models.pc import PCStatus
from backend.app.models.alert import AlertType, AlertSeverity
from backend.app.sockets.manager import emit_metrics_update, emit_status_change, emit_alert

settings = get_settings()


async def run_poller():
    """
    Main polling loop. Runs every WS_PUSH_INTERVAL seconds.
    - Checks connectivity for each node
    - Collects metrics for online nodes
    - Detects offline transitions and creates alerts
    - Pushes updates via WebSocket
    """
    print(f"🕵️ Background Poller started (interval: {settings.WS_PUSH_INTERVAL}s)")

    while True:
        try:
            async with async_session_factory() as db:
                nodes = await NodeService.get_all_nodes(db)

                for node in nodes:
                    hostname = node["hostname"]
                    old_status = node["status"]

                    if hostname == "localhost":
                        await NodeService.update_node_status(db, hostname, "online")
                        continue

                    # Check connectivity
                    is_online = await AnsibleService.check_connection(hostname)
                    new_status = PCStatus.ONLINE.value if is_online else PCStatus.OFFLINE.value

                    # Detect status transition
                    if old_status != new_status:
                        await emit_status_change(hostname, new_status)

                        # Create alert on offline transition
                        if new_status == PCStatus.OFFLINE.value:
                            pc = await NodeService.get_node_by_hostname(db, hostname)
                            if pc:
                                await AlertService.create_alert(
                                    db, pc.id, AlertType.PC_OFFLINE.value,
                                    f"{hostname} went offline",
                                    AlertSeverity.WARNING.value)
                                await emit_alert({
                                    "type": "pc_offline", "hostname": hostname,
                                    "message": f"{hostname} went offline",
                                    "severity": "warning"})

                    if is_online:
                        # Collect metrics
                        result = await AnsibleService.run_playbook(
                            "collect_metrics.yml", hostname)
                        if result.get("status") == "success" and "data" in result:
                            metrics = AnsibleService.parse_metrics_from_playbook(
                                result["data"], hostname)
                            if metrics:
                                await NodeService.update_node_status(
                                    db, hostname, "online", {
                                        "cpu_load": metrics["cpu_load"],
                                        "ram_percentage": metrics["ram_percentage"],
                                        "disk_percentage": metrics["disk_percentage"],
                                    })

                                # Store in history
                                pc = await NodeService.get_node_by_hostname(db, hostname)
                                if pc:
                                    try:
                                        await MetricsService.store_snapshot(
                                            db, pc.id,
                                            float(metrics.get("cpu_load", 0)),
                                            int(metrics.get("ram_used", 0)),
                                            int(metrics.get("ram_total", 1)),
                                            float(str(metrics.get("disk_percentage", "0%")).replace("%", "")))
                                    except (ValueError, TypeError):
                                        pass

                                    # High resource alerts
                                    try:
                                        cpu = float(metrics.get("cpu_load", 0))
                                        if cpu > 4.0:
                                            await AlertService.create_alert(
                                                db, pc.id, AlertType.HIGH_CPU.value,
                                                f"{hostname} CPU load: {cpu}",
                                                AlertSeverity.WARNING.value)
                                            await emit_alert({
                                                "type": "high_cpu", "hostname": hostname,
                                                "message": f"High CPU: {cpu}"})
                                    except (ValueError, TypeError):
                                        pass

                                # Push to WebSocket
                                await emit_metrics_update({
                                    "hostname": hostname, "status": "online",
                                    "metrics": metrics})
                        else:
                            await NodeService.update_node_status(db, hostname, "online")
                    else:
                        await NodeService.update_node_status(
                            db, hostname, "offline", {})

                await db.commit()

        except Exception as e:
            print(f"❌ Poller error: {e}")

        await asyncio.sleep(settings.WS_PUSH_INTERVAL)


async def run_time_sync():
    """Background time sync — runs every hour. Preserved from original."""
    print("🕒 Background Time Sync service initiated.")
    while True:
        try:
            print("🕒 Running time sync...")
            await AnsibleService.run_playbook("sync_time.yml", "all")
        except Exception as e:
            print(f"Time sync error: {e}")
        await asyncio.sleep(3600)
