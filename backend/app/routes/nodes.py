"""
Nodes Router
=============
PC/node management endpoints.
Backward-compatible with original: GET /api/nodes, POST /api/nodes/add
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.services.node_service import NodeService
from backend.app.schemas.pc_schema import (
    PCCreate, PCBulkAddRequest, PCListResponse, PCResponse, PCAssignLabRequest,
)

router = APIRouter(prefix="/api", tags=["nodes"])


@router.get("/nodes")
async def get_nodes(db: AsyncSession = Depends(get_db)):
    """
    List all nodes with status & metrics.
    Backward-compatible: returns {"nodes": [...]}
    """
    nodes = await NodeService.get_all_nodes(db)
    stats = await NodeService.get_stats(db)
    return {"nodes": nodes, **stats}


@router.post("/nodes/add")
async def add_node(request: PCCreate, db: AsyncSession = Depends(get_db)):
    """
    Add a single node. Backward-compatible with original endpoint.
    """
    try:
        pc = await NodeService.create_node(
            db=db,
            hostname=request.hostname,
            username=request.user,
            password=request.password,
            ip=request.ip,
            lab_id=request.lab_id,
        )
        return {"status": "success", "message": f"Node {pc.hostname} added", "id": pc.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/nodes/bulk-add")
async def bulk_add_nodes(request: PCBulkAddRequest,
                         db: AsyncSession = Depends(get_db)):
    """Bulk add PCs via CSV data, paste text, or IP range."""
    if request.method == "ip_range" and request.ip_range:
        ips = NodeService.expand_ip_range(request.ip_range)
        entries = [{"hostname": ip, "ip": ip,
                    "username": request.default_username or "student"}
                   for ip in ips]
    elif request.pcs:
        entries = [pc.model_dump() for pc in request.pcs]
    else:
        raise HTTPException(status_code=400, detail="No PC data provided")

    result = await NodeService.bulk_create_nodes(
        db=db, entries=entries,
        default_password=request.default_password or "changeme",
        default_lab_id=request.default_lab_id)
    return result


@router.post("/nodes/bulk-add/csv")
async def bulk_add_csv(file: UploadFile = File(...),
                       db: AsyncSession = Depends(get_db)):
    """Upload a CSV file for bulk PC import."""
    content = await file.read()
    csv_text = content.decode("utf-8")
    valid, invalid = NodeService.parse_csv(csv_text)

    # Check duplicates
    hostnames = [e["hostname"] for e in valid]
    duplicates = await NodeService.check_duplicates(db, hostnames)

    return {
        "valid": [e for e in valid if e["hostname"] not in duplicates],
        "duplicates": duplicates,
        "invalid": invalid,
        "total": len(valid) + len(invalid),
    }


@router.post("/nodes/assign-lab")
async def assign_nodes_to_lab(request: PCAssignLabRequest,
                              db: AsyncSession = Depends(get_db)):
    """Assign or move PCs to a lab."""
    count = 0
    from backend.app.services.lab_service import LabService
    count = await LabService.assign_pcs_to_lab(db, request.pc_ids, request.lab_id)
    return {"status": "success", "updated": count}


@router.delete("/nodes/{pc_id}")
async def delete_node(pc_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a PC from the system."""
    pc = await NodeService.get_node_by_id(db, pc_id)
    if not pc:
        raise HTTPException(status_code=404, detail="PC not found")
    await NodeService.delete_node(db, pc)
    return {"status": "success", "message": f"Node {pc.hostname} deleted"}
