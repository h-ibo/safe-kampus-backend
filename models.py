from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from database import Base
from datetime import datetime

class Olay(Base):
    __tablename__ = "olaylar"

    id = Column(Integer, primary_key=True, index=True)
    olay_turu = Column(String(100), nullable=False)
    konum = Column(String(150), nullable=False)
    aciklama = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
