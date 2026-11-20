from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
from app.models.experiment import Experiment, ExperimentCategory

class ExperimentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_categories(self) -> List[ExperimentCategory]:
        stmt = select(ExperimentCategory).order_by(ExperimentCategory.display_order)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_experiments(self, category_id: Optional[UUID] = None) -> List[Experiment]:
        stmt = select(Experiment)
        if category_id:
            stmt = stmt.where(Experiment.category_id == category_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_slug(self, slug: str) -> Optional[Experiment]:
        stmt = select(Experiment).where(Experiment.slug == slug)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, exp_id: UUID) -> Optional[Experiment]:
        stmt = select(Experiment).where(Experiment.id == exp_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
