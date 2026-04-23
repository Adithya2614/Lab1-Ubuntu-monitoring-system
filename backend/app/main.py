"""
WMI Backend — Main Application Entry Point
=============================================
FastAPI application with Socket.IO, database lifecycle,
background tasks, and all route registration.
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import get_settings
from backend.app.database import init_db, close_db
from backend.app.sockets.manager import socket_app

# Import all routers
from backend.app.routes.nodes import router as nodes_router
from backend.app.routes.actions import router as actions_router
from backend.app.routes.labs import router as labs_router
from backend.app.routes.alerts import router as alerts_router
from backend.app.routes.audit import router as audit_router
from backend.app.routes.metrics import router as metrics_router
from backend.app.routes.settings import router as settings_router
from backend.app.routes.reports import router as reports_router

# Import background tasks
from backend.app.tasks.poller import run_poller, run_time_sync

settings = get_settings()


# --- Application Lifespan ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages startup and shutdown events.
    Replaces deprecated @app.on_event decorators.
    """
    # Startup
    print("🚀 WMI Backend starting up...")
    await init_db()
    print("✅ Database initialized")

    # Start background tasks
    poller_task = asyncio.create_task(run_poller())
    sync_task = asyncio.create_task(run_time_sync())

    yield  # Application runs here

    # Shutdown
    print("🛑 WMI Backend shutting down...")
    poller_task.cancel()
    sync_task.cancel()
    await close_db()


# --- FastAPI Application ---

app = FastAPI(
    title="WMI — Ubuntu Lab Monitoring System",
    version="2.0.0",
    description="Production-grade monitoring and management dashboard for Ubuntu lab PCs",
    lifespan=lifespan,
)

# --- CORS ---

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Register Routers ---

app.include_router(nodes_router)
app.include_router(actions_router)
app.include_router(labs_router)
app.include_router(alerts_router)
app.include_router(audit_router)
app.include_router(metrics_router)
app.include_router(settings_router)
app.include_router(reports_router)

# --- Mount Socket.IO ---

app.mount("/ws", socket_app)

# --- Health Check (backward-compatible) ---

@app.get("/")
def health_check():
    return {"status": "ok", "service": "WMI — Ubuntu Lab Monitoring System", "version": "2.0.0"}


# --- Entrypoint ---

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True,
    )
