"""
Actions Router
===============
Action execution endpoints.
Backward-compatible: POST /api/action
New: POST /api/actions/bulk
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.services.action_engine import ActionEngine
from backend.app.schemas.action_schema import ActionRequest, BulkActionRequest


router = APIRouter(prefix="/api", tags=["actions"])


@router.post("/action")
async def execute_action(request: ActionRequest,
                         db: AsyncSession = Depends(get_db)):
    """
    Execute a single action on a target node.
    Fully backward-compatible with original POST /api/action.
    """
    result = await ActionEngine.execute_single(
        db=db, target=request.target,
        action_type=request.action_type,
        parameters=request.parameters)

    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.post("/actions/bulk")
async def execute_bulk_action(request: BulkActionRequest,
                              db: AsyncSession = Depends(get_db)):
    """Execute an action across multiple PCs in parallel."""
    result = await ActionEngine.execute_bulk(
        db=db, targets=request.targets,
        action_type=request.action_type,
        parameters=request.parameters)
    return result
