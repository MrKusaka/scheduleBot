from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Boolean, Time, Date, ForeignKey, BigInteger

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
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    date = Column(Date, nullable=True)
    day = Column(String, nullable=True)
    work_start = Column(Time, nullable=True)
    work_end = Column(Time, nullable=True)



# Создание таблиц
async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)