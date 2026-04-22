from fastapi import APIRouter, HTTPException
from controller.services.ansible_service import AnsibleService
from controller.api.models import ActionRequest, MetricData, Node, AddNodeRequest

router = APIRouter(prefix="/api")

@router.get("/nodes", response_model=dict)
def get_nodes():
    nodes = AnsibleService.get_nodes()
    # In a real app, we would merge this with cached status from a database
    return {"nodes": nodes}

@router.post("/metrics")
def receive_metrics(data: MetricData):
    # Retrieve metrics from node (pushed) or Ansible output
    # For now, just print or cache in memory
    print(f"Received metrics for {data.node_id}: {data.metrics}")
    return {"status": "received"}

@router.post("/action")
def execute_action(request: ActionRequest):
    # Map action_type to playbook
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
        "restrict_websites": "restrict_websites.yml"
    }
    
    playbook = playbook_map.get(request.action_type)
    if not playbook:
        raise HTTPException(status_code=400, detail=f"Unknown action type: {request.action_type}")
        
    # Inject action-specific defaults
    params = request.parameters.copy() if request.parameters else {}
    if request.action_type == "remove_package":
        params["state"] = "absent"
    elif request.action_type == "install_package":
        params["state"] = "present"
    
    # Rename 'action' to 'browser_action' for browse management
    if request.action_type == "manage_browsers" and "action" in params:
        params["browser_action"] = params.pop("action")
        
    result = AnsibleService.run_playbook(playbook, request.target, params)
    
    # Update cache if successful
    if result.get("status") == "success":
        # Mark online
        AnsibleService.update_cache(request.target, status="online")
        
        # 1. Handle Metrics Collection
        if request.action_type == "collect_metrics" and "data" in result:
             try:
                 data = result["data"]
                 if data and "plays" in data and data["plays"]:
                     tasks = data["plays"][0].get("tasks", [])
                     metrics_task = next((t for t in tasks if t.get("task", {}).get("name") == "Return Metrics"), None)
                     
                     if metrics_task and "hosts" in metrics_task and request.target in metrics_task["hosts"]:
                         msg = metrics_task["hosts"][request.target].get("msg", {})
                         
                         # Calculate percentages for dashboard summary
                         ram_p = 0
                         try:
                             used = int(msg.get("ram_used", 0))
                             total = int(msg.get("ram_total", 1))
                             ram_p = int((used / total) * 100)
                         except:
                             pass
                             
                         disk_p = msg.get("disk_usage", "0%")
                         
                         # Cache simplified facts for the dashboard card
                         facts = {
                             "cpu_load": msg.get("cpu_load", "0.00"),
                             "ram_percentage": f"{ram_p}%",
                             "disk_percentage": disk_p
                         }
                         AnsibleService.update_cache(request.target, metrics=facts)
             except Exception as e:
                 print(f"Failed to cache metrics: {e}")

        # 2. Handle File Listing
        if request.action_type == "list_files" and "data" in result:
             try:
                 data = result["data"]
                 if data and "plays" in data and data["plays"]:
                     tasks = data["plays"][0].get("tasks", [])
                     task = next((t for t in tasks if t.get("task", {}).get("name") == "Return Files"), None)
                     if task and "hosts" in task and request.target in task["hosts"]:
                         raw_lines = task["hosts"][request.target].get("msg", [])
                         parsed_files = []
                         # Simple parsing of ls -la --full-time
                         for line in raw_lines:
                             parts = line.split(maxsplit=8)
                             if len(parts) >= 9:
                                 is_dir = parts[0].startswith('d')
                                 # size is index 4, date is 5, time is 6, name is 8
                                 name = parts[8]
                                 if name == "." or name == "..": continue
                                 files_list_item = {
                                     "name": name,
                                     "type": "directory" if is_dir else "file",
                                     "size": parts[4],
                                     "modified": f"{parts[5]} {parts[6].split('.')[0]}",
                                     "permissions": parts[0]
                                 }
                                 parsed_files.append(files_list_item)
                         
                         result["data"] = parsed_files
             except Exception as e:
                 print(f"Failed to parse files: {e}")

        # 3. Handle Package Listing
        if request.action_type == "list_packages" and "data" in result:
             try:
                 data = result["data"]
                 if data and "plays" in data and data["plays"]:
                     tasks = data["plays"][0].get("tasks", [])
                     task = next((t for t in tasks if t.get("task", {}).get("name") == "Return Packages"), None)
                     if task and "hosts" in task and request.target in task["hosts"]:
                         raw_lines = task["hosts"][request.target].get("msg", [])
                         parsed_pkgs = []
                         # format: Package Version Status
                         for line in raw_lines:
                             parts = line.split()
                             if len(parts) >= 3:
                                 parsed_pkgs.append({
                                     "name": parts[0],
                                     "version": parts[1],
                                     "status": " ".join(parts[2:]),
                                     "publisher": "Ubuntu/Debian", # Placeholder
                                     "size": "-" 
                                 })
                         result["data"] = parsed_pkgs
             except Exception as e:
                 print(f"Failed to parse packages: {e}")

        # 4. Handle Archive Manifest
        if request.action_type in ["archive_files", "get_vault"] and "data" in result:
             try:
                 data = result["data"]
                 if data and "plays" in data and data["plays"]:
                     tasks = data["plays"][0].get("tasks", [])
                     task = next((t for t in tasks if t.get("task", {}).get("name") == "Output Result"), None)
                     if task and "hosts" in task and request.target in task["hosts"]:
                         manifest = task["hosts"][request.target].get("msg", [])
                         AnsibleService.update_cache(request.target, vault_manifest=manifest)
                         result["data"] = manifest
             except Exception as e:
                 print(f"Failed to parse archive manifest: {e}")

        if request.action_type == "restore_files":
             AnsibleService.update_cache(request.target, vault_manifest=[])

        # 5. Handle Cleanup Apps
        if request.action_type == "cleanup_apps" and "data" in result:
             try:
                 data = result["data"]
                 if data and "plays" in data and data["plays"]:
                     tasks = data["plays"][0].get("tasks", [])
                     task = next((t for t in tasks if t.get("task", {}).get("name") == "Output Result"), None)
                     if task and "hosts" in task and request.target in task["hosts"]:
                         cleanup_data = task["hosts"][request.target].get("msg", {})
                         
                         # Log the deletion to a file
                         removed_pkgs = cleanup_data.get("removed_packages", [])
                         if removed_pkgs:
                             try:
                                 import datetime, os
                                 log_dir = "/home/cse-icb-060/WMI/logs"
                                 log_file = os.path.join(log_dir, "app_removal.log")
                                 timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                 with open(log_file, "a") as f:
                                     f.write(f"[{timestamp}] PC: {request.target}\n")
                                     f.write(f"Removed ({len(removed_pkgs)}): {', '.join(removed_pkgs)}\n\n")
                             except Exception as log_e:
                                 print(f"Failed to write removal log: {log_e}")

                         result["data"] = cleanup_data
             except Exception as e:
                 print(f"Failed to parse cleanup data: {e}")

    return result

@router.post("/nodes/add")
def add_node(request: AddNodeRequest):
    success = AnsibleService.add_node(
        hostname=request.hostname,
        user=request.user,
        password=request.password,
        ip=request.ip
    )
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add node to inventory")
    return {"status": "success", "message": f"Node {request.hostname} added"}

@router.get("/audit")
def get_audit_logs():
    import os
    log_file = "/home/cse-icb-060/WMI/logs/app_removal.log"
    if not os.path.exists(log_file):
        return {"logs": []}
    
    try:
        with open(log_file, "r") as f:
            lines = f.readlines()
        
        logs = []
        current_entry = {}
        for line in lines:
            line = line.strip()
            if not line: continue
            
            if line.startswith("[") and "PC:" in line:
                timestamp = line.split("]")[0][1:]
                pc = line.split("PC:")[1].strip()
                current_entry = {"timestamp": timestamp, "pc": pc}
            elif line.startswith("Removed"):
                current_entry["removed"] = line.split(":", 1)[1].strip()
                logs.append(current_entry)
        
        return {"logs": logs[::-1]} # Most recent first
    except Exception as e:
        print(f"Failed to read logs: {e}")
        return {"logs": []}

