from config import DATABASE_URL

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import create_engine, Column, Integer, String, select
# from sqlalchemy.orm import sessionmaker, Session, Mapped, mapped_column

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = async_sessionmaker(engine)


class Base(DeclarativeBase):
    pass
