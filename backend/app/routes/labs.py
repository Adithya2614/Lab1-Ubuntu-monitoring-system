"""
Labs Router
============
Lab management CRUD endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.services.lab_service import LabService
from backend.app.schemas.lab_schema import LabCreate, LabUpdate


router = APIRouter(prefix="/api/labs", tags=["labs"])


@router.get("")
async def list_labs(db: AsyncSession = Depends(get_db)):
    labs = await LabService.get_all_labs(db)
    return {"labs": labs, "total": len(labs)}


@router.post("")
async def create_lab(request: LabCreate, db: AsyncSession = Depends(get_db)):
    existing = await LabService.get_lab_by_name(db, request.name)
    if existing:
        raise HTTPException(status_code=409, detail="Lab name already exists")
    lab = await LabService.create_lab(db, request.name, request.description)
    return {"status": "success", "id": lab.id, "name": lab.name}


@router.get("/{lab_id}")
async def get_lab(lab_id: int, db: AsyncSession = Depends(get_db)):
    lab = await LabService.get_lab_by_id(db, lab_id)
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    from backend.app.models.pc import PCStatus
    return {
        "id": lab.id, "name": lab.name, "description": lab.description,
        "layout": lab.layout, "created_at": lab.created_at,
        "pc_count": len(lab.pcs),
        "online_count": sum(1 for p in lab.pcs if p.status == PCStatus.ONLINE.value),
        "pcs": [{
            "id": p.id, "hostname": p.hostname, "name": p.hostname,
            "ip": p.ip, "status": p.status, "facts": p.cached_metrics,
        } for p in lab.pcs],
    }


@router.put("/{lab_id}")
async def update_lab(lab_id: int, request: LabUpdate,
                     db: AsyncSession = Depends(get_db)):
    lab = await LabService.get_lab_by_id(db, lab_id)
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    data = request.model_dump(exclude_unset=True)
    await LabService.update_lab(db, lab, **data)
    return {"status": "success", "id": lab.id}


@router.delete("/{lab_id}")
async def delete_lab(lab_id: int, db: AsyncSession = Depends(get_db)):
    lab = await LabService.get_lab_by_id(db, lab_id)
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    await LabService.delete_lab(db, lab)
    return {"status": "success"}


@router.put("/{lab_id}/layout")
async def save_lab_layout(lab_id: int, layout: dict,
                          db: AsyncSession = Depends(get_db)):
    lab = await LabService.get_lab_by_id(db, lab_id)
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    await LabService.save_layout(db, lab, layout)
    return {"status": "success"}
