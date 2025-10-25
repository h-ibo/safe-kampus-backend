# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# PostgreSQL bağlantı URL'si
DATABASE_URL = "postgresql://safekampus_user:Kartal1903!@localhost:5432/safekampus_db"

# Engine oluştur
engine = create_engine(DATABASE_URL)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class (tablolar bundan türeyecek)
Base = declarative_base()
