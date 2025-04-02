from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, BigInteger, String, Time, ForeignKey

from config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)


class WorkTime(Base):
    __tablename__ = "work_time"

    id = Column(Integer, primary_key=True, autoincrement=True)
    day = Column(String, nullable=True)
    work_start = Column(Time, nullable=True)
    work_end = Column(Time, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)


# Создание таблиц
async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)