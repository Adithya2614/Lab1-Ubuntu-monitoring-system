import subprocess
import json
import os
import threading
import time
from typing import List, Dict, Any

ANSIBLE_DIR = os.path.abspath("ansible")
INVENTORY_FILE = os.path.join(ANSIBLE_DIR, "inventory", "hosts")
PLAYBOOKS_DIR = os.path.join(ANSIBLE_DIR, "playbooks")

# Simple in-memory cache for node status and metrics
# Structure: { "node_id": { "status": "online", "last_seen": timestamp, "metrics": {} } }
NODE_CACHE = {}

class AnsibleService:
    @staticmethod
    def get_nodes() -> List[Dict[str, Any]]:
        """
        Parses the inventory and merges with cached status.
        """
        try:
            cmd = ["ansible-inventory", "-i", INVENTORY_FILE, "--list"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            inventory = json.loads(result.stdout)
            
            nodes = []
            
            def extract_hosts(group_data):
                hosts_found = []
                if "hosts" in group_data:
                    for hostname in group_data["hosts"]:
                        # Get cached data
                        cached = NODE_CACHE.get(hostname, {})
                        status = cached.get("status", "unknown")
                        facts = cached.get("metrics", {})
                        
                        hosts_found.append({
                            "id": hostname, 
                            "name": hostname, 
                            "status": status,
                            "facts": facts,
                            "vault_manifest": cached.get("vault_manifest", [])
                        })
                return hosts_found

            if "ubuntu_nodes" in inventory:
               nodes.extend(extract_hosts(inventory["ubuntu_nodes"]))
            elif "all" in inventory:
                 # Fallback
                 if "children" in inventory["all"]:
                     for child in inventory["all"]["children"]:
                         if child != "ungrouped":
                             nodes.extend(extract_hosts(inventory.get(child, {})))
            
            # Remove duplicates
            unique_nodes = {n["id"]: n for n in nodes}.values()
            return list(unique_nodes)

        except subprocess.CalledProcessError as e:
            print(f"Error reading inventory: {e.stderr}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []

    @staticmethod
    def update_cache(node_id: str, status: str = None, metrics: dict = None, vault_manifest: list = None):
        if node_id not in NODE_CACHE:
            NODE_CACHE[node_id] = {}
        
        if status:
            NODE_CACHE[node_id]["status"] = status
        
        if metrics is not None:
            # Parse flat metrics from playbook if needed, or just store
            # The structure from collect_metrics is flat keys (cpu_load, etc.)
            NODE_CACHE[node_id]["metrics"] = metrics

        if vault_manifest is not None:
            NODE_CACHE[node_id]["vault_manifest"] = vault_manifest

    @staticmethod
    def run_playbook(playbook_name: str, target: str, extra_vars: Dict[str, Any] = None) -> Dict[str, Any]:
        playbook_path = os.path.join(PLAYBOOKS_DIR, playbook_name)
        if not os.path.exists(playbook_path):
            return {"status": "error", "message": f"Playbook {playbook_name} not found"}

        cmd = ["ansible-playbook", "-i", INVENTORY_FILE, playbook_path, "--limit", target]
        
        if extra_vars:
            cmd.extend(["--extra-vars", json.dumps(extra_vars)])

        
        # Run locally? We might need connection=local for localhost, handled in inventory.
        env = os.environ.copy()
        env["ANSIBLE_STDOUT_CALLBACK"] = "json"
        
        try:
            # We run asynchronously in a real app, but for now synchronous/subprocess
            result = subprocess.run(cmd, capture_output=True, text=True, env=env)
            
            try:
                # Try to parse the stdout as JSON if the callback worked
                json_output = json.loads(result.stdout)
                return {
                    "status": "success" if result.returncode == 0 else "failure",
                    "data": json_output,
                    "raw_stdout": result.stdout
                }
            except json.JSONDecodeError:
                 return {
                    "status": "success" if result.returncode == 0 else "failure",
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def check_connection(target: str) -> bool:
        """Simple ping check via Ansible"""
        if target == "localhost": return True
        try:
            # Step 1: ICMP Ping (Fast)
            # Find the IP first if possible
            cmd_inventory = ["ansible-inventory", "-i", INVENTORY_FILE, "--host", target]
            inv_res = subprocess.run(cmd_inventory, capture_output=True, text=True)
            ip = target
            if inv_res.returncode == 0:
                host_vars = json.loads(inv_res.stdout)
                ip = host_vars.get("ansible_host", target)

            ping_res = subprocess.run(["ping", "-c", "1", "-W", "1", ip], stdout=subprocess.DEVNULL)
            if ping_res.returncode != 0:
                return False

            # Step 2: Ansible Ping (Reliable SSH check)
            cmd = ["ansible", target, "-i", INVENTORY_FILE, "-m", "ping", "--timeout", "3"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return "SUCCESS" in result.stdout
        except:
            return False

    @staticmethod
    def add_node(hostname: str, user: str, password: str, ip: str = None) -> bool:
        """Adds a new host to the inventory file."""
        try:
            # Ensure hostname has .local if needed (optional)
            if not hostname.endswith(".local") and "." not in hostname:
                hostname += ".local"
                
            entry = f"{hostname} "
            if ip:
                entry += f"ansible_host={ip} "
            entry += f"ansible_user={user} ansible_python_interpreter=/usr/bin/python3 ansible_become_pass={password}\n"
            
            with open(INVENTORY_FILE, 'a') as f:
                f.write(entry)
            
            # Immediately trigger a status check so it doesn't show as 'offline/unknown'
            def quick_check():
                is_online = AnsibleService.check_connection(hostname)
                AnsibleService.update_cache(hostname, status="online" if is_online else "offline")
            
            threading.Thread(target=quick_check, daemon=True).start()
            
            return True
        except Exception as e:
            print(f"Error adding node: {e}")
            return False

    @classmethod
    def start_background_polling(cls):
        """Starts a background thread to poll node statuses."""
        def poll():
            while True:
                nodes = cls.get_nodes()
                for node in nodes:
                    node_id = node["id"]
                    if node_id == "localhost":
                        cls.update_cache(node_id, status="online")
                        continue
                    
                    # 1. Check Connectivity
                    is_online = cls.check_connection(node_id)
                    
                    if is_online:
                        cls.update_cache(node_id, status="online")
                        # 2. If online, fetch metrics in background
                        # Use a separate thread so one slow PC doesn't block the whole poller
                        threading.Thread(target=cls.refresh_node_metrics, args=(node_id,), daemon=True).start()
                    else:
                        # CLEAR metrics if offline so we don't show old stale data
                        cls.update_cache(node_id, status="offline", metrics={})
                
                # Wait 15 seconds before next poll
                time.sleep(15)

        thread = threading.Thread(target=poll, daemon=True)
        thread.start()
        print("🕵️ Smart Background Poller started (Status + Metrics).")

    @classmethod
    def refresh_node_metrics(cls, node_id: str):
        """Internal helper to fetch metrics for a node in the background."""
        try:
            # We reuse the collect_metrics playbook
            # We use a simplified version of the logic in router.py
            result = cls.run_playbook("collect_metrics.yml", node_id)
            if result.get("status") == "success" and "data" in result:
                data = result["data"]
                if data and "plays" in data and data["plays"]:
                    tasks = data["plays"][0].get("tasks", [])
                    metrics_task = next((t for t in tasks if t.get("task", {}).get("name") == "Return Metrics"), None)
                    
                    if metrics_task and "hosts" in metrics_task and node_id in metrics_task["hosts"]:
                        msg = metrics_task["hosts"][node_id].get("msg", {})
                        
                        ram_p = 0
                        try:
                            used = int(msg.get("ram_used", 0))
                            total = int(msg.get("ram_total", 1))
                            ram_p = int((used / total) * 100)
                        except: pass
                            
                        facts = {
                            "cpu_load": msg.get("cpu_load", "0.00"),
                            "ram_percentage": f"{ram_p}%",
                            "disk_percentage": msg.get("disk_usage", "0%"),
                            "last_refresh": time.strftime("%H:%M:%S")
                        }
                        cls.update_cache(node_id, metrics=facts)
        except Exception as e:
            print(f"Background metric fetch failed for {node_id}: {e}")
    @classmethod
    def start_background_time_sync(cls):
        """Starts a background thread to sync time/timezone once an hour."""
        def sync_loop():
            while True:
                print("🕒 Background Time Sync started...")
                cls.run_playbook("sync_time.yml", "all")
                # Wait 1 hour
                time.sleep(3600)
        
        threading.Thread(target=sync_loop, daemon=True).start()
        print("🕒 Background Time Sync service initiated.")
