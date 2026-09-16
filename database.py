import enum
import os

from dotenv import load_dotenv
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


class PointStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Point(Base):
    __tablename__ = "points"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    district = Column(String, nullable=False)
    address = Column(String, nullable=False)
    hours = Column(String, nullable=True)
    rules = Column(String, nullable=True)
    is_active = Column(Boolean, default=False)
    status = Column(SAEnum(PointStatus), default=PointStatus.PENDING)
    created_by = Column(Integer, nullable=True)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
