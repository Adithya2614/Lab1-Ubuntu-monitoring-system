"""
Ansible Service (Refactored)
==============================
Core Ansible runner — refactored from the original controller/services/ansible_service.py.
Now uses asyncio subprocess for non-blocking execution and reads config from environment.
All original functionality is preserved.
"""

import asyncio
import json
import os
import re
from typing import Any, Dict, List, Optional

from backend.app.config import get_settings

settings = get_settings()


class AnsibleService:
    """
    Handles all interactions with Ansible: running playbooks, parsing inventory,
    checking connections, and managing the inventory file.
    """

    # ------------------------------------------------------------------
    # Playbook Execution
    # ------------------------------------------------------------------

    @staticmethod
    async def run_playbook(
        playbook_name: str,
        target: str,
        extra_vars: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Run an Ansible playbook against a target host.
        Returns parsed JSON output when available, raw stdout otherwise.
        """
        playbook_path = os.path.join(settings.PLAYBOOKS_DIR, playbook_name)
        if not os.path.exists(playbook_path):
            return {"status": "error", "message": f"Playbook {playbook_name} not found"}

        cmd = [
            "ansible-playbook",
            "-i", settings.INVENTORY_FILE,
            playbook_path,
            "--limit", target,
        ]

        if extra_vars:
            cmd.extend(["--extra-vars", json.dumps(extra_vars)])

        env = os.environ.copy()
        env["ANSIBLE_STDOUT_CALLBACK"] = "json"
        env["ANSIBLE_CONFIG"] = os.path.join(settings.ANSIBLE_DIR_ABS, "ansible.cfg")

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )
            stdout, stderr = await process.communicate()
            stdout_text = stdout.decode("utf-8", errors="replace")
            stderr_text = stderr.decode("utf-8", errors="replace")

            try:
                json_output = json.loads(stdout_text)
                return {
                    "status": "success" if process.returncode == 0 else "failure",
                    "data": json_output,
                    "raw_stdout": stdout_text,
                }
            except json.JSONDecodeError:
                return {
                    "status": "success" if process.returncode == 0 else "failure",
                    "stdout": stdout_text,
                    "stderr": stderr_text,
                    "returncode": process.returncode,
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ------------------------------------------------------------------
    # Connection Check
    # ------------------------------------------------------------------

    @staticmethod
    async def check_connection(target: str) -> bool:
        """
        Two-stage connectivity check: ICMP ping → Ansible SSH ping.
        Returns True if the host is reachable and SSH is working.
        """
        if target == "localhost":
            return True

        try:
            # Step 1: Resolve IP from inventory
            ip = target
            cmd_inv = [
                "ansible-inventory", "-i", settings.INVENTORY_FILE,
                "--host", target,
            ]
            proc = await asyncio.create_subprocess_exec(
                *cmd_inv,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            if proc.returncode == 0:
                host_vars = json.loads(stdout.decode())
                ip = host_vars.get("ansible_host", target)

            # Step 2: ICMP Ping (fast, 1 second timeout)
            ping_proc = await asyncio.create_subprocess_exec(
                "ping", "-c", "1", "-W", "1", ip,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await ping_proc.communicate()
            if ping_proc.returncode != 0:
                return False

            # Step 3: Ansible SSH Ping (reliable)
            ssh_cmd = [
                "ansible", target,
                "-i", settings.INVENTORY_FILE,
                "-m", "ping",
                "--timeout", "3",
            ]
            ssh_proc = await asyncio.create_subprocess_exec(
                *ssh_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await ssh_proc.communicate()
            return "SUCCESS" in stdout.decode()
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Inventory Parsing
    # ------------------------------------------------------------------

    @staticmethod
    async def get_inventory_hosts() -> List[Dict[str, Any]]:
        """
        Parse the Ansible inventory file and return a list of host dictionaries.
        Each dict contains: hostname, ansible_host (IP), ansible_user, group.
        """
        try:
            cmd = [
                "ansible-inventory", "-i", settings.INVENTORY_FILE, "--list",
            ]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            inventory = json.loads(stdout.decode())

            hosts = []
            hostvars = inventory.get("_meta", {}).get("hostvars", {})

            # Iterate through all groups (except meta groups)
            for group_name, group_data in inventory.items():
                if group_name.startswith("_") or group_name == "all":
                    continue
                if isinstance(group_data, dict) and "hosts" in group_data:
                    for hostname in group_data["hosts"]:
                        vars_dict = hostvars.get(hostname, {})
                        hosts.append({
                            "hostname": hostname,
                            "ip": vars_dict.get("ansible_host"),
                            "username": vars_dict.get("ansible_user", ""),
                            "group": group_name,
                        })

            return hosts
        except Exception as e:
            print(f"Error parsing inventory: {e}")
            return []

    # ------------------------------------------------------------------
    # Inventory Modification
    # ------------------------------------------------------------------

    @staticmethod
    async def add_host_to_inventory(
        hostname: str,
        username: str,
        password: str,
        ip: Optional[str] = None,
        group: str = "ubuntu_nodes",
    ) -> bool:
        """
        Appends a new host entry to the Ansible inventory file.
        Preserves the existing format and group structure.
        """
        try:
            # Ensure .local suffix for mDNS resolution
            if not hostname.endswith(".local") and "." not in hostname:
                hostname += ".local"

            entry = f"{hostname} "
            if ip:
                entry += f"ansible_host={ip} "
            entry += (
                f"ansible_user={username} "
                f"ansible_python_interpreter=/usr/bin/python3 "
                f"ansible_become_pass={password}\n"
            )

            # Read existing file to find the right group section
            with open(settings.INVENTORY_FILE, "r") as f:
                content = f.read()

            # Check if group exists
            group_header = f"[{group}]"
            if group_header in content:
                # Append to end of file (under existing group)
                with open(settings.INVENTORY_FILE, "a") as f:
                    f.write(entry)
            else:
                # Create new group section
                with open(settings.INVENTORY_FILE, "a") as f:
                    f.write(f"\n{group_header}\n{entry}")

            return True
        except Exception as e:
            print(f"Error adding host to inventory: {e}")
            return False

    @staticmethod
    async def remove_host_from_inventory(hostname: str) -> bool:
        """Remove a host entry from the inventory file."""
        try:
            with open(settings.INVENTORY_FILE, "r") as f:
                lines = f.readlines()

            # Filter out lines starting with the hostname
            new_lines = [
                line for line in lines
                if not line.strip().startswith(hostname)
            ]

            with open(settings.INVENTORY_FILE, "w") as f:
                f.writelines(new_lines)

            return True
        except Exception as e:
            print(f"Error removing host from inventory: {e}")
            return False

    # ------------------------------------------------------------------
    # Metric Parsing Helpers (preserved from original router.py logic)
    # ------------------------------------------------------------------

    @staticmethod
    def parse_metrics_from_playbook(data: dict, target: str) -> Optional[dict]:
        """
        Extract metrics from collect_metrics.yml playbook output.
        Preserved from original router.py lines 66-94.
        """
        try:
            if data and "plays" in data and data["plays"]:
                tasks = data["plays"][0].get("tasks", [])
                metrics_task = next(
                    (t for t in tasks if t.get("task", {}).get("name") == "Return Metrics"),
                    None,
                )
                if metrics_task and "hosts" in metrics_task and target in metrics_task["hosts"]:
                    msg = metrics_task["hosts"][target].get("msg", {})

                    ram_p = 0
                    try:
                        used = int(msg.get("ram_used", 0))
                        total = int(msg.get("ram_total", 1))
                        ram_p = int((used / total) * 100)
                    except (ValueError, ZeroDivisionError):
                        pass

                    return {
                        "uptime": msg.get("uptime", "-"),
                        "cpu_load": msg.get("cpu_load", "0.00"),
                        "ram_used": msg.get("ram_used", "0"),
                        "ram_total": msg.get("ram_total", "0"),
                        "ram_percentage": f"{ram_p}%",
                        "disk_percentage": msg.get("disk_usage", "0%"),
                    }
        except Exception as e:
            print(f"Failed to parse metrics: {e}")
        return None

    @staticmethod
    def parse_files_from_playbook(data: dict, target: str) -> Optional[list]:
        """
        Parse file listing from list_files.yml playbook output.
        Preserved from original router.py lines 97-125.
        """
        try:
            if data and "plays" in data and data["plays"]:
                tasks = data["plays"][0].get("tasks", [])
                task = next(
                    (t for t in tasks if t.get("task", {}).get("name") == "Return Files"),
                    None,
                )
                if task and "hosts" in task and target in task["hosts"]:
                    raw_lines = task["hosts"][target].get("msg", [])
                    parsed_files = []
                    for line in raw_lines:
                        parts = line.split(maxsplit=8)
                        if len(parts) >= 9:
                            is_dir = parts[0].startswith("d")
                            name = parts[8]
                            if name in (".", ".."):
                                continue
                            parsed_files.append({
                                "name": name,
                                "type": "directory" if is_dir else "file",
                                "size": parts[4],
                                "modified": f"{parts[5]} {parts[6].split('.')[0]}",
                                "permissions": parts[0],
                            })
                    return parsed_files
        except Exception as e:
            print(f"Failed to parse files: {e}")
        return None

    @staticmethod
    def parse_packages_from_playbook(data: dict, target: str) -> Optional[list]:
        """
        Parse package listing from get_packages.yml playbook output.
        Preserved from original router.py lines 128-150.
        """
        try:
            if data and "plays" in data and data["plays"]:
                tasks = data["plays"][0].get("tasks", [])
                task = next(
                    (t for t in tasks if t.get("task", {}).get("name") == "Return Packages"),
                    None,
                )
                if task and "hosts" in task and target in task["hosts"]:
                    raw_lines = task["hosts"][target].get("msg", [])
                    parsed_pkgs = []
                    for line in raw_lines:
                        parts = line.split()
                        if len(parts) >= 3:
                            parsed_pkgs.append({
                                "name": parts[0],
                                "version": parts[1],
                                "status": " ".join(parts[2:]),
                                "publisher": "Ubuntu/Debian",
                                "size": "-",
                            })
                    return parsed_pkgs
        except Exception as e:
            print(f"Failed to parse packages: {e}")
        return None

    @staticmethod
    def parse_vault_from_playbook(data: dict, target: str) -> Optional[list]:
        """
        Parse vault manifest from archive/get_vault playbook output.
        Preserved from original router.py lines 152-164.
        """
        try:
            if data and "plays" in data and data["plays"]:
                tasks = data["plays"][0].get("tasks", [])
                task = next(
                    (t for t in tasks if t.get("task", {}).get("name") == "Output Result"),
                    None,
                )
                if task and "hosts" in task and target in task["hosts"]:
                    return task["hosts"][target].get("msg", [])
        except Exception as e:
            print(f"Failed to parse vault: {e}")
        return None

    @staticmethod
    def parse_cleanup_from_playbook(data: dict, target: str) -> Optional[dict]:
        """
        Parse cleanup results from cleanup_apps.yml playbook output.
        Preserved from original router.py lines 169-195.
        """
        try:
            if data and "plays" in data and data["plays"]:
                tasks = data["plays"][0].get("tasks", [])
                task = next(
                    (t for t in tasks if t.get("task", {}).get("name") == "Output Result"),
                    None,
                )
                if task and "hosts" in task and target in task["hosts"]:
                    return task["hosts"][target].get("msg", {})
        except Exception as e:
            print(f"Failed to parse cleanup: {e}")
        return None
