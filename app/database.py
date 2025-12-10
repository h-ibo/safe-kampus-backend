from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql+asyncpg://safekampus_user:Kartal1903!@localhost/safekampus_db"

# Async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Oturum oluşturucu
SessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

# Base sınıfı (model sınıfları buradan türetilir)
Base = declarative_base()
