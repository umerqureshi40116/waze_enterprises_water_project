from sqlalchemy import Column, String, DateTime, Float, Text, Integer, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base

class WeeklyReport(Base):
    __tablename__ = "weekly_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    week_start = Column(DateTime, nullable=False)
    week_end = Column(DateTime, nullable=False)
    year = Column(Integer, nullable=False)
    week_number = Column(Integer, nullable=False)
    
    # Sales metrics
    sales_revenue = Column(Float, default=0.0)
    purchase_costs = Column(Float, default=0.0)
    blow_costs = Column(Float, default=0.0)
    waste_recovery = Column(Float, default=0.0)
    
    # Calculated values
    total_revenue = Column(Float, default=0.0)
    total_costs = Column(Float, default=0.0)
    profit = Column(Float, default=0.0)
    profit_margin = Column(Float, default=0.0)
    
    # Summary
    total_transactions = Column(Integer, default=0)
    summary = Column(Text)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    generated_by = Column(String, ForeignKey("users.id"))
    
    class Config:
        from_attributes = True
