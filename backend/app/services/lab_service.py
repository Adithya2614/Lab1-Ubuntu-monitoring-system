"""
Lab Service
============
Business logic for lab CRUD and PC assignment.
"""

from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.models.lab import Lab
from backend.app.models.pc import PC, PCStatus


class LabService:
    """Handles lab management operations."""

    @staticmethod
    async def get_all_labs(db: AsyncSession) -> list[dict]:
        """Get all labs with PC counts."""
        stmt = select(Lab).options(selectinload(Lab.pcs)).order_by(Lab.name)
        result = await db.execute(stmt)
        labs = result.scalars().all()
        return [{
            "id": lab.id, "name": lab.name, "description": lab.description,
            "layout": lab.layout, "created_at": lab.created_at,
            "updated_at": lab.updated_at,
            "pc_count": len(lab.pcs),
            "online_count": sum(1 for pc in lab.pcs if pc.status == PCStatus.ONLINE.value),
        } for lab in labs]

    @staticmethod
    async def get_lab_by_id(db: AsyncSession, lab_id: int) -> Optional[Lab]:
        stmt = select(Lab).options(selectinload(Lab.pcs)).where(Lab.id == lab_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_lab_by_name(db: AsyncSession, name: str) -> Optional[Lab]:
        stmt = select(Lab).where(Lab.name == name)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_lab(db: AsyncSession, name: str,
                         description: Optional[str] = None) -> Lab:
        lab = Lab(name=name, description=description)
        db.add(lab)
        await db.flush()
        return lab

    @staticmethod
    async def update_lab(db: AsyncSession, lab: Lab, **kwargs) -> Lab:
        for key, value in kwargs.items():
            if hasattr(lab, key) and value is not None:
                setattr(lab, key, value)
        await db.flush()
        return lab

    @staticmethod
    async def delete_lab(db: AsyncSession, lab: Lab) -> bool:
        # Unassign PCs before deleting
        for pc in lab.pcs:
            pc.lab_id = None
        await db.delete(lab)
        await db.flush()
        return True

    @staticmethod
    async def assign_pcs_to_lab(db: AsyncSession, pc_ids: list[int],
                                 lab_id: Optional[int]) -> int:
        """Assign or unassign PCs to/from a lab. Returns count of updated PCs."""
        count = 0
        for pc_id in pc_ids:
            pc = await db.get(PC, pc_id)
            if pc:
                pc.lab_id = lab_id
                count += 1
        await db.flush()
        return count

    @staticmethod
    async def save_layout(db: AsyncSession, lab: Lab, layout: dict) -> Lab:
        """Save drag-and-drop room layout configuration."""
        lab.layout = layout
        await db.flush()
        return lab
