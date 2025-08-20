
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Example Render URL (must include +asyncpg and sslmode=require):
# postgresql+asyncpg://USER:PASSWORD@HOST:5432/DBNAME?sslmode=require
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://whome_user:w5O1SxiKRCIA9C4Coj0QDDmwSGd8oGBO@dpg-d2i2qlu3jp1c738v2f90-a/whome")

engine = create_async_engine(DATABASE_URL, echo=False, future=True, pool_pre_ping=True)

AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False, autocommit=False)

Base = declarative_base()

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
