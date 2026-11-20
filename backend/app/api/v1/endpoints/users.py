from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, UserProfile
from app.models.report import Subscription
from app.schemas.user import UserResponse, UserProfileResponse, SubscriptionResponse

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    profile_stmt = select(UserProfile).where(UserProfile.user_id == current_user.id)
    profile_res = await db.execute(profile_stmt)
    profile = profile_res.scalar_one_or_none()

    sub_stmt = select(Subscription).where(Subscription.user_id == current_user.id)
    sub_res = await db.execute(sub_stmt)
    subscription = sub_res.scalar_one_or_none()

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        is_verified=current_user.is_verified,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        profile=UserProfileResponse.model_validate(profile) if profile else None,
        subscription=SubscriptionResponse.model_validate(subscription) if subscription else None
    )
