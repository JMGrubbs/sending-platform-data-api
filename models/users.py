from dependencies import Base
from sqlalchemy import Column, Integer, String, Boolean, select
from sqlalchemy.orm import Mapped
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession


class UserModel(Base):
    __tablename__ = "users"
    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    username: Mapped[str] = Column(String, unique=True, index=True)
    password: Mapped[str] = Column(String)
    email: Mapped[str] = Column(String, unique=True, index=True)
    full_name: Mapped[str] = Column(String)
    disabled: Mapped[bool] = Column(Boolean, default=False)
    created_at: Mapped[str] = Column(String)
    updated_at: Mapped[str] = Column(String)


class Users(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    disabled: bool
    created_at: Optional[str]
    updated_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    class Config:
        orm_mode = True

    async def get_users(db: AsyncSession):
        users = db.query(UserModel).all()
        result = await db.execute(select(users))
        users = result.scalars().all()
        return users

    async def create_user(db: AsyncSession, new_user: dict):
        db_user = UserModel(**new_user)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
