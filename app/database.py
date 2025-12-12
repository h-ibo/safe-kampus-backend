from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Veritabanı URL
DATABASE_URL = "postgresql+asyncpg://safekampus_user:Kartal1903!@localhost/safekampus_db"

# Async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Session oluşturucu
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class
Base = declarative_base()


# FastAPI'nin her endpoint için DB oturumu oluşturup kapatmasını sağlayan fonksiyon
async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
