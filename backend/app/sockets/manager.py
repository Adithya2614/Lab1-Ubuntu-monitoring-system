"""
WebSocket Manager
==================
Socket.IO server for real-time push updates.
Hybrid model: periodic metrics (every N seconds) + instant event push.
"""

import socketio
from backend.app.config import get_settings

settings = get_settings()

# Create Socket.IO async server
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",  # Restricted in production
    logger=False,
    engineio_logger=False,
)

# ASGI app wrapper for mounting onto FastAPI
socket_app = socketio.ASGIApp(sio, socketio_path="/ws/socket.io")


# --- Connection Events ---

@sio.event
async def connect(sid, environ):
    """Client connected."""
    print(f"🔌 WebSocket client connected: {sid}")


@sio.event
async def disconnect(sid):
    """Client disconnected."""
    print(f"🔌 WebSocket client disconnected: {sid}")


@sio.event
async def subscribe_lab(sid, data):
    """Client subscribes to a specific lab's updates."""
    lab_id = data.get("lab_id")
    if lab_id:
        await sio.enter_room(sid, f"lab_{lab_id}")
        print(f"📡 Client {sid} subscribed to lab_{lab_id}")


@sio.event
async def subscribe_pc(sid, data):
    """Client subscribes to a specific PC's updates."""
    pc_id = data.get("pc_id")
    if pc_id:
        await sio.enter_room(sid, f"pc_{pc_id}")


# --- Emitter Functions (called from background tasks) ---

async def emit_metrics_update(pc_data: dict):
    """Broadcast metric update to all connected clients."""
    await sio.emit("metrics_update", pc_data)


async def emit_status_change(pc_hostname: str, new_status: str):
    """Instant push when a PC goes online/offline."""
    await sio.emit("status_change", {
        "hostname": pc_hostname, "status": new_status
    })


async def emit_alert(alert_data: dict):
    """Instant push for new alerts."""
    await sio.emit("new_alert", alert_data)


async def emit_action_progress(batch_id: str, progress: dict):
    """Push bulk action progress updates."""
    await sio.emit("action_progress", {
        "batch_id": batch_id, **progress
    })


async def emit_toast(message: str, toast_type: str = "info"):
    """Push a toast notification to all clients."""
    await sio.emit("toast", {"message": message, "type": toast_type})
