import os
from dotenv import load_dotenv
# Eksik olan SQLAlchemy importlarını buraya ekledik:
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# override=True ekleyerek eski sistem önbelleğini zorla eziyoruz
load_dotenv(override=True)

# Doğrudan lokal veritabanına kilitledik
DATABASE_URL = os.getenv("DATABASE_URL")

# Lokal bağlantılarda şifreleme/SSL zorunluluğu olmadığı için tertemiz bağlanır
engine = create_async_engine(
    DATABASE_URL, 
    echo=True  # Terminalde tabloların oluşma sorgularını izleyebilirsin
)

SessionLocal = sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()