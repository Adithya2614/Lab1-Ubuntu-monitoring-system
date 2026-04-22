import os
import subprocess
import re
import socket
from concurrent.futures import ThreadPoolExecutor

HOSTS_FILE = "/home/cse-icb-060/WMI/ansible/inventory/hosts"
# Define the IP ranges to scan based on your network setup
IP_RANGES = ["172.111.0", "172.111.1", "172.111.2", "172.111.3"]

def get_ip_by_ping(hostname):
    """Try to get IP via standard .local resolution first."""
    try:
        # Try both uppercase and lowercase as mDNS is picky
        for name in [hostname, hostname.lower()]:
            if not name.endswith(".local"):
                name += ".local"
            result = subprocess.run(["getent", "hosts", name], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.split()[0]
    except:
        pass
    return None

def scan_ip(ip):
    """Check if an IP is up and return its hostname if found."""
    try:
        # Quick ping check (wait 200ms)
        subprocess.run(["ping", "-c", "1", "-W", "0.2", ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Try to resolve hostname for the UP IP
        result = subprocess.run(["getent", "hosts", ip], capture_output=True, text=True)
        if result.returncode == 0:
            return ip, result.stdout.split()[-1].replace(".local", "").upper()
    except:
        pass
    return ip, None

def discover_network():
    print("🔍 Searching for PCs on the network...")
    active_hosts = {}
    
    # Scan all ranges in parallel for speed
    all_ips = [f"{r}.{i}" for r in IP_RANGES for i in range(1, 255)]
    with ThreadPoolExecutor(max_workers=100) as executor:
        results = executor.map(scan_ip, all_ips)
        for ip, hostname in results:
            if hostname:
                active_hosts[hostname] = ip
    
    return active_hosts

def update_ansible_hosts():
    if not os.path.exists(HOSTS_FILE):
        print(f"❌ Hosts file not found at {HOSTS_FILE}")
        return

    # First, scan the network
    network_map = discover_network()
    
    with open(HOSTS_FILE, 'r') as f:
        lines = f.readlines()

    updated_lines = []
    changes_made = False

    for line in lines:
        # Check if line contains a PC entry (e.g. CSE-ICB-051.local)
        match = re.search(r'^(CSE-ICB-\d+)', line, re.IGNORECASE)
        if match:
            hostname = match.group(1).upper()
            
            # 1. Try .local resolution first
            found_ip = get_ip_by_ping(hostname)
            
            # 2. If .local failed, check our network scan results
            if not found_ip:
                found_ip = network_map.get(hostname)
            
            if found_ip:
                # Update or add ansible_host parameter
                if "ansible_host=" in line:
                    new_line = re.sub(r'ansible_host=[^\s]+', f'ansible_host={found_ip}', line)
                else:
                    parts = line.split()
                    parts.insert(1, f'ansible_host={found_ip}')
                    new_line = " ".join(parts) + "\n"
                
                if new_line != line:
                    print(f"✅ Found {hostname} at {found_ip}")
                    updated_lines.append(new_line)
                    changes_made = True
                    continue
            else:
                print(f"⚠️  Could not find IP for {hostname}")
        
        updated_lines.append(line)

    if changes_made:
        with open(HOSTS_FILE, 'w') as f:
            f.writelines(updated_lines)
        print("💾 Updated inventory file with new IPs.")
    else:
        print("🙌 No IP changes detected.")

if __name__ == "__main__":
    update_ansible_hosts()
