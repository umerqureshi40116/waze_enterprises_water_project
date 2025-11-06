from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base

class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(String, ForeignKey("items.id"))
    movement_type = Column(String, nullable=False)  # 'purchase', 'sale', 'production', 'waste', 'adjustment'
    quantity_change = Column(Integer, nullable=False)
    reference_id = Column(String)
    before_quantity = Column(Integer)
    after_quantity = Column(Integer)
    recorded_by = Column(String, ForeignKey("users.id"))
    movement_date = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text)
