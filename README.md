# 🖥️ WMI — Web-based Monitoring Interface for Ubuntu Lab PCs

A centralized, web-based monitoring and management dashboard for Ubuntu computer lab environments. WMI uses **Ansible** for agentless remote execution, a **FastAPI** backend as the control plane, and a **React + Vite** frontend for a modern, real-time dashboard experience.

> Built for college/university computer labs where administrators need to monitor, manage, and enforce policies across dozens of Ubuntu workstations from a single interface — without installing agents on each machine.

---

## ✨ Features

### 📊 Real-Time Monitoring
- **Live system metrics** — CPU load, RAM usage, disk utilization per PC
- **Auto-polling** — Background thread refreshes node status and metrics every 15 seconds
- **Online/Offline detection** — Two-stage connectivity check (ICMP ping → Ansible SSH ping)

### 📁 Remote File Management
- **File browser** — List files on any remote PC's home directory
- **File deletion** — Delete files remotely from the dashboard
- **Secure Vault (Archive)** — Move non-whitelisted user files to an encrypted vault (`.wmi_vault`) with a full manifest for recovery
- **Restore** — Restore archived files back to their original locations

### 📦 Package & Application Management
- **List installed packages** — View all dpkg-managed packages on any node
- **Install / Remove packages** — Trigger `apt` operations remotely
- **Whitelist-based Cleanup** — Bulk remove all packages not present in `app_whitelist.json`, with a hardcoded safety list to protect critical system packages
- **Audit logging** — Every app removal is logged with timestamp and target PC

### 🌐 Network & Internet Control
- **Enable / Disable internet** — Toggle outgoing network access via UFW firewall rules
- **Website restriction** — Whitelist-only browsing mode: block all websites except those in `website_whitelist.txt`
- **Browser management** — Start, stop, or manage browser processes remotely

### 🕒 System Administration
- **Automatic time sync** — Background service syncs time/timezone across all nodes every hour
- **Network discovery** — Auto-discover PCs on the network and update Ansible inventory with current IPs
- **Add new PCs** — Dynamically add new nodes to the inventory via the dashboard UI

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────┐
│                  Browser                     │
│           React + Vite Dashboard             │
│              (port 5173)                     │
└──────────────┬───────────────────────────────┘
               │  REST API (JSON)
               ▼
┌──────────────────────────────────────────────┐
│           FastAPI Controller                 │
│              (port 8000)                     │
│                                              │
│  ┌─────────────┐  ┌──────────────────────┐   │
│  │  API Router  │  │  AnsibleService      │   │
│  │  /api/nodes  │  │  • Background Poller │   │
│  │  /api/action │  │  • Time Sync         │   │
│  │  /api/audit  │  │  • In-Memory Cache   │   │
│  └─────────────┘  └──────────────────────┘   │
└──────────────┬───────────────────────────────┘
               │  SSH (via Ansible)
               ▼
┌──────────────────────────────────────────────┐
│          Ubuntu Lab PCs (Nodes)              │
│                                              │
│   CSE-ICB-051  CSE-ICB-052  CSE-ICB-053 ... │
│                                              │
│   No agents required — Ansible connects      │
│   over SSH using inventory credentials       │
└──────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
WMI/
├── controller/                  # FastAPI backend (Python)
│   ├── main.py                  # App entrypoint, CORS, startup events
│   ├── requirements.txt         # Python dependencies
│   ├── api/
│   │   ├── router.py            # All REST API endpoints
│   │   └── models.py            # Pydantic request/response models
│   └── services/
│       └── ansible_service.py   # Ansible integration, caching, polling
│
├── dashboard/                   # React frontend (Vite)
│   ├── package.json             # Node dependencies
│   ├── vite.config.js           # Vite configuration
│   ├── index.html               # HTML entrypoint
│   └── src/
│       ├── App.jsx              # Root component with routing
│       ├── api.js               # API client (fetch wrapper)
│       ├── main.jsx             # React DOM render
│       ├── index.css            # Global styles
│       ├── context/
│       │   └── AppContext.jsx   # React context provider
│       └── components/
│           ├── Layout.jsx       # App shell / navigation
│           ├── Dashboard.jsx    # Main dashboard grid view
│           ├── PCCard.jsx       # Individual PC summary card
│           ├── PCDetail.jsx     # Detailed PC management view
│           ├── AddPCModal.jsx   # Modal to add new nodes
│           └── AuditLog.jsx     # App removal audit log viewer
│
├── ansible/                     # Ansible configuration & playbooks
│   ├── ansible.cfg              # Ansible settings
│   ├── inventory/
│   │   └── hosts                # Node inventory (hostnames, IPs, creds)
│   └── playbooks/
│       ├── collect_metrics.yml      # CPU, RAM, disk metrics
│       ├── list_files.yml           # List home directory files
│       ├── delete_files.yml         # Delete remote files
│       ├── archive_files.yml        # Archive user files to vault
│       ├── restore_files.yml        # Restore files from vault
│       ├── get_vault.yml            # Retrieve vault manifest
│       ├── get_packages.yml         # List installed packages
│       ├── manage_packages.yml      # Install/remove packages
│       ├── cleanup_apps.yml         # Whitelist-based bulk cleanup
│       ├── generate_app_whitelist.yml  # Generate whitelist from current state
│       ├── manage_internet.yml      # Enable/disable internet (UFW)
│       ├── manage_browsers.yml      # Browser process management
│       ├── restrict_websites.yml    # Whitelist-only website access
│       └── sync_time.yml            # Time/timezone synchronization
│
├── config/                      # Policy configuration files
│   ├── app_whitelist.json       # Allowed packages (for cleanup)
│   └── website_whitelist.txt    # Allowed websites (for restriction)
│
├── logs/                        # Runtime logs
│   └── app_removal.log          # Audit trail of package removals
│
├── discovery.py                 # Network scanner to auto-update inventory IPs
├── start.sh                     # One-command startup script (both servers)
└── START_SERVER.md              # Detailed server startup instructions
```

---

## 🚀 Getting Started

### Prerequisites

| Requirement       | Version   | Purpose                    |
|--------------------|-----------|----------------------------|
| **Python**         | 3.8+      | Backend (FastAPI)          |
| **Node.js**        | 20+       | Frontend (Vite 7)          |
| **Ansible**        | 2.10+     | Remote execution engine    |
| **SSH access**     | —         | Connectivity to lab PCs    |
| **Ubuntu**         | 20.04+    | Target nodes (lab PCs)     |

### 1. Clone & Setup

```bash
git clone <repository-url>
cd WMI

# Create Python virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r controller/requirements.txt

# Install frontend dependencies
cd dashboard
npm install
cd ..
```

### 2. Configure Inventory

Edit `ansible/inventory/hosts` to add your lab PCs:

```ini
[ubuntu_nodes]
localhost ansible_connection=local ansible_python_interpreter=/usr/bin/python3
PC-001.local ansible_user=labuser ansible_python_interpreter=/usr/bin/python3 ansible_become_pass=password123
PC-002.local ansible_host=192.168.1.50 ansible_user=labuser ansible_python_interpreter=/usr/bin/python3 ansible_become_pass=password123
```

### 3. Start Both Servers

```bash
./start.sh
```

Or start them manually in two terminals:

```bash
# Terminal 1 — Backend
./.venv/bin/python3 -m controller.main
# → http://localhost:8000

# Terminal 2 — Frontend
cd dashboard && npm run dev
# → http://localhost:5173
```

### 4. Open the Dashboard

Navigate to **http://localhost:5173** in your browser.

---

## 🔌 API Reference

All endpoints are prefixed with `/api`.

| Method | Endpoint        | Description                           |
|--------|-----------------|---------------------------------------|
| GET    | `/api/nodes`    | List all nodes with status & metrics  |
| POST   | `/api/action`   | Execute an action on a target node    |
| POST   | `/api/nodes/add`| Add a new node to the inventory       |
| GET    | `/api/audit`    | Retrieve app removal audit logs       |
| GET    | `/`             | Health check                          |

### Action Types (`POST /api/action`)

```json
{
  "target": "CSE-ICB-051.local",
  "action_type": "<action>",
  "parameters": { }
}
```

| Action                   | Description                          | Parameters                     |
|--------------------------|--------------------------------------|--------------------------------|
| `collect_metrics`        | Fetch CPU, RAM, disk stats           | —                              |
| `list_files`             | List files in home directory         | `{ "path": "/home/user" }`     |
| `delete_files`           | Delete specified files               | `{ "files": [...] }`           |
| `archive_files`          | Move user files to vault             | —                              |
| `restore_files`          | Restore files from vault             | —                              |
| `get_vault`              | Get vault manifest                   | —                              |
| `list_packages`          | List installed packages              | —                              |
| `install_package`        | Install a package via apt            | `{ "package_name": "vim" }`    |
| `remove_package`         | Uninstall a package                  | `{ "package_name": "vim" }`    |
| `cleanup_apps`           | Remove non-whitelisted packages      | —                              |
| `generate_app_whitelist` | Generate whitelist from current PC   | —                              |
| `update_internet`        | Toggle internet access               | `{ "state": "enabled" }`      |
| `manage_browsers`        | Manage browser processes             | `{ "action": "stop" }`        |
| `restrict_websites`      | Website whitelist enforcement        | `{ "target_state": "restrict" }`|
| `sync_time`              | Sync time and timezone               | —                              |

Interactive API docs available at **http://localhost:8000/docs** (Swagger UI).

---

## 🔒 Security Notes

- **SSH-based** — All remote operations use SSH (no custom agents). Ensure SSH keys or password auth is properly configured.
- **Credentials in inventory** — `ansible_become_pass` is stored in plaintext in the hosts file. For production, use [Ansible Vault](https://docs.ansible.com/ansible/latest/vault_guide/index.html) to encrypt sensitive data.
- **CORS** — Currently set to `allow_origins=["*"]` for development. Restrict this in production.
- **Firewall rules** — Internet control and website restriction use UFW. SSH (port 22) and the controller API (port 8000) are always allowed to maintain connectivity.

---

## ⚙️ Background Services

The FastAPI backend starts two background threads on startup:

| Service              | Interval  | Purpose                                         |
|----------------------|-----------|--------------------------------------------------|
| **Status Poller**    | 15 sec    | Checks online/offline status and fetches metrics |
| **Time Sync**        | 1 hour    | Synchronizes system time across all nodes        |

---

## 🛠️ Tech Stack

| Layer      | Technology                              |
|------------|------------------------------------------|
| Frontend   | React 19, React Router 7, Vite 7, Lucide Icons |
| Backend    | FastAPI, Uvicorn, Pydantic               |
| Automation | Ansible (playbooks, inventory, ad-hoc)   |
| Transport  | SSH (OpenSSH)                            |
| Firewall   | UFW (Uncomplicated Firewall)             |
| Discovery  | Python (ICMP ping, mDNS, `getent`)      |

---

## 📄 License

This project was built for internal use in a university computer lab environment.

---

<p align="center">
  Made with ❤️ for lab administrators who deserve better tools.
</p>
