"""Settings Router — SSH keys, whitelist, blocked apps."""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.models.whitelist import WhitelistDomain
from backend.app.models.blocked_app import BlockedApp
from backend.app.models.ssh_key import SSHKey
from backend.app.schemas.settings_schema import (
    SSHKeyCreate, WhitelistDomainCreate, WhitelistBulkImportRequest,
    BlockedAppCreate, BlockedAppUpdate)

router = APIRouter(prefix="/api/settings", tags=["settings"])

# --- Whitelist ---
@router.get("/whitelist")
async def list_whitelist(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WhitelistDomain).order_by(WhitelistDomain.domain))
    return {"domains": [{"id": d.id, "domain": d.domain, "lab_id": d.lab_id,
        "created_at": d.created_at} for d in result.scalars().all()]}

@router.post("/whitelist")
async def add_whitelist(req: WhitelistDomainCreate, db: AsyncSession = Depends(get_db)):
    d = WhitelistDomain(domain=req.domain.lower().strip(), lab_id=req.lab_id)
    db.add(d); await db.flush()
    return {"status": "success", "id": d.id}

@router.post("/whitelist/bulk")
async def bulk_whitelist(req: WhitelistBulkImportRequest, db: AsyncSession = Depends(get_db)):
    for d in req.domains:
        db.add(WhitelistDomain(domain=d.lower().strip(), lab_id=req.lab_id))
    await db.flush()
    return {"status": "success", "imported": len(req.domains)}

@router.delete("/whitelist/{did}")
async def del_whitelist(did: int, db: AsyncSession = Depends(get_db)):
    d = await db.get(WhitelistDomain, did)
    if not d: raise HTTPException(404, "Not found")
    await db.delete(d); await db.flush()
    return {"status": "success"}

# --- Blocked Apps ---
@router.get("/blocked-apps")
async def list_blocked(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BlockedApp).order_by(BlockedApp.app_name))
    return {"apps": [{"id": a.id, "app_name": a.app_name, "lab_id": a.lab_id,
        "auto_kill": a.auto_kill, "created_at": a.created_at} for a in result.scalars().all()]}

@router.post("/blocked-apps")
async def add_blocked(req: BlockedAppCreate, db: AsyncSession = Depends(get_db)):
    a = BlockedApp(app_name=req.app_name.lower().strip(), lab_id=req.lab_id, auto_kill=req.auto_kill)
    db.add(a); await db.flush()
    return {"status": "success", "id": a.id}

@router.delete("/blocked-apps/{aid}")
async def del_blocked(aid: int, db: AsyncSession = Depends(get_db)):
    a = await db.get(BlockedApp, aid)
    if not a: raise HTTPException(404, "Not found")
    await db.delete(a); await db.flush()
    return {"status": "success"}

# --- SSH Keys ---
@router.get("/ssh-keys")
async def list_keys(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SSHKey).order_by(SSHKey.created_at.desc()))
    return {"keys": [{"id": k.id, "name": k.name, "public_key": k.public_key,
        "fingerprint": k.fingerprint, "created_at": k.created_at} for k in result.scalars().all()]}

@router.post("/ssh-keys")
async def gen_key(req: SSHKeyCreate, db: AsyncSession = Depends(get_db)):
    import subprocess, os
    key_dir = os.path.join(os.path.abspath("."), ".ssh_keys")
    os.makedirs(key_dir, exist_ok=True)
    kp = os.path.join(key_dir, req.name)
    r = subprocess.run(["ssh-keygen","-t","rsa","-b","4096","-f",kp,"-N","","-C",f"wmi-{req.name}"],
        capture_output=True, text=True)
    if r.returncode != 0: raise HTTPException(500, f"Key gen failed: {r.stderr}")
    with open(f"{kp}.pub") as f: pub = f.read().strip()
    fp = subprocess.run(["ssh-keygen","-lf",f"{kp}.pub"], capture_output=True, text=True)
    key = SSHKey(name=req.name, public_key=pub, private_key_path=kp,
        fingerprint=fp.stdout.strip() if fp.returncode==0 else None)
    db.add(key); await db.flush()
    return {"status": "success", "id": key.id, "public_key": pub}

@router.delete("/ssh-keys/{kid}")
async def del_key(kid: int, db: AsyncSession = Depends(get_db)):
    k = await db.get(SSHKey, kid)
    if not k: raise HTTPException(404, "Not found")
    import os
    for ext in ("", ".pub"):
        p = f"{k.private_key_path}{ext}"
        if os.path.exists(p): os.remove(p)
    await db.delete(k); await db.flush()
    return {"status": "success"}
