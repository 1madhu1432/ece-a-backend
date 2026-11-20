from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime

class UserProfileResponse(BaseModel):
    id: UUID
    full_name: str
    college_name: Optional[str]
    branch: Optional[str]
    academic_year: Optional[int]
    avatar_url: Optional[str]

    class Config:
        from_attributes = True

class SubscriptionResponse(BaseModel):
    tier: str
    monthly_execution_quota: int
    monthly_ai_token_quota: int
    quota_reset_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    role: str
    is_verified: bool
    is_active: bool
    profile: Optional[UserProfileResponse] = None
    subscription: Optional[SubscriptionResponse] = None
    created_at: datetime

    class Config:
        from_attributes = True
