from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # 'preform', 'bottle', 'sold'
    size = Column(String, nullable=False)  # '500ml', '1500ml', etc.
    grade = Column(String, nullable=False)  # 'A', 'B', 'C'
    unit = Column(String, nullable=False, default='pcs')  # 'pcs', 'kg', 'liters', etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Stock(Base):
    __tablename__ = "stocks"

    item_id = Column(String, ForeignKey("items.id"), primary_key=True)
    quantity = Column(Integer, nullable=False, default=0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
