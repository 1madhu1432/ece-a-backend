from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from uuid import UUID
from app.models.user import User, UserProfile
from app.models.report import Subscription
from datetime import datetime, timezone, timedelta

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email.lower())
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(
        self, 
        email: str, 
        hashed_password: str, 
        full_name: str, 
        college_name: Optional[str] = None, 
        branch: str = "ECE", 
        academic_year: int = 3,
        role: str = "student"
    ) -> User:
        user = User(
            email=email.lower(),
            hashed_password=hashed_password,
            role=role,
            is_verified=True # Auto-verify in development
        )
        self.db.add(user)
        await self.db.flush()

        profile = UserProfile(
            user_id=user.id,
            full_name=full_name,
            college_name=college_name,
            branch=branch,
            academic_year=academic_year
        )
        self.db.add(profile)

        subscription = Subscription(
            user_id=user.id,
            tier="free",
            monthly_execution_quota=100,
            monthly_ai_token_quota=50000,
            quota_reset_at=datetime.now(timezone.utc) + timedelta(days=30),
            is_active=True
        )
        self.db.add(subscription)

        await self.db.commit()
        await self.db.refresh(user)
        return user
