from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import Optional
from uuid import UUID
from app.repositories.user_repo import UserRepository
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.models.user import User

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def register(
        self, 
        email: str, 
        password: str, 
        full_name: str, 
        college_name: Optional[str] = None, 
        branch: str = "ECE", 
        academic_year: int = 3
    ) -> User:
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email address already exists."
            )

        hashed_pw = get_password_hash(password)
        user = await self.user_repo.create_user(
            email=email,
            hashed_password=hashed_pw,
            full_name=full_name,
            college_name=college_name,
            branch=branch,
            academic_year=academic_year
        )
        return user

    async def authenticate(self, email: str, password: str) -> dict:
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user
        }
