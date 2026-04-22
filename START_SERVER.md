# 🚀 How to Start the Local Server

> ⚠️ **Before starting, check if the servers are already running:**
> ```bash
> curl http://localhost:8000/   # Backend check
> curl http://localhost:5173    # Frontend check
> ```
> If they respond, you're good to go — no need to start them again!

---

## ✅ Easiest Way — One Command (Recommended)

Run this from the project root to start **both** servers at once:

```bash
cd /home/cse-icb-060/WMI
./start.sh
```

Press `Ctrl+C` to stop both servers.

---

## Manual Start (Two Terminals)

This project has **two** servers that need to be running:

1. **Backend Controller** — FastAPI (Python) on port `8000`
2. **Frontend Dashboard** — Vite + React on port `5173`

### Terminal 1 — Backend (FastAPI)

```bash
cd /home/cse-icb-060/WMI
./.venv/bin/python3 -m controller.main
```

- Runs on: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

### Terminal 2 — Frontend (Vite)

> ⚠️ Requires **Node.js 20+**. Use the full nvm source command below (not just `nvm use 20`).

```bash
export NVM_DIR="$HOME/.nvm" && \. "$NVM_DIR/nvm.sh" && nvm use 20
cd /home/cse-icb-060/WMI/dashboard
npm run dev
```

- Runs on: `http://localhost:5173`

---

## 🔧 Troubleshooting

### `Command 'nvm' not found`
`nvm` is a shell function, not a binary. You must source it first:
```bash
export NVM_DIR="$HOME/.nvm" && \. "$NVM_DIR/nvm.sh"
nvm use 20
```
Or just use `./start.sh` which handles this automatically.

### `[Errno 98] Address already in use`
A server is already running on that port:
```bash
# Kill whatever is using port 8000 (backend)
kill $(lsof -t -i:8000)

# Kill whatever is using port 5173 (frontend)
kill $(lsof -t -i:5173)
```
Then start again.

---

## Quick Reference

| Service    | Command                                         | URL                        |
|------------|-------------------------------------------------|----------------------------|
| **Both**   | `./start.sh`                                    | —                          |
| Backend    | `./.venv/bin/python3 -m controller.main`        | http://localhost:8000      |
| Frontend   | `source nvm && nvm use 20 && npm run dev`       | http://localhost:5173      |


This project has **two** servers that need to be running:

1. **Backend Controller** — FastAPI (Python) on port `8000`
2. **Frontend Dashboard** — Vite + React on port `5173`

---

## Prerequisites

Make sure you're in the project root directory:

```bash
cd /home/cse-icb-060/WMI
```

---

## 1. Start the Backend Controller (FastAPI)

> Run this in **Terminal 1**

```bash
./.venv/bin/python3 -m controller.main
```

- Runs on: `http://localhost:8000`
- Health check: `http://localhost:8000/`
- API docs: `http://localhost:8000/docs`

---

## 2. Start the Frontend Dashboard (Vite)

> Run this in **Terminal 2**

> ⚠️ **Requires Node.js 20+** (Vite 7 does not support Node 18). Use `nvm` to switch versions.

```bash
cd /home/cse-icb-060/WMI/dashboard
nvm use 20
npm run dev
```

If `nvm` is not loaded yet (e.g. in a fresh terminal), run:
```bash
export NVM_DIR="$HOME/.nvm" && \. "$NVM_DIR/nvm.sh" && nvm use 20
cd /home/cse-icb-060/WMI/dashboard && npm run dev
```

- Runs on: `http://localhost:5173`
- Open this URL in your browser to access the dashboard.

---

## ✅ Verify Both Servers Are Running

```bash
# Check backend
curl http://localhost:8000/

# Check frontend (should return HTML)
curl http://localhost:5173
```

---

## 🛑 Stop the Servers

Press `Ctrl + C` in each terminal to stop the respective server.

---

## 🔧 Troubleshooting

### `[Errno 98] Address already in use`

This means a server is already running on that port. Either:
- **Use the existing server** (just open the URL in your browser), or
- **Kill the process and restart:**

```bash
# Kill whatever is using port 8000 (backend)
kill $(lsof -t -i:8000)

# Kill whatever is using port 5173 (frontend)
kill $(lsof -t -i:5173)
```

Then start the servers again using the commands above.

---

## Quick Reference

| Service    | Command                                      | URL                        |
|------------|----------------------------------------------|----------------------------|
| Backend    | `./.venv/bin/python3 -m controller.main`     | http://localhost:8000      |
| Frontend   | `cd dashboard && npm run dev`                | http://localhost:5173      |
