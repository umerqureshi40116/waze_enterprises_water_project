from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ItemBase(BaseModel):
    name: str
    type: str  # 'preform', 'bottle', 'sold'
    size: str
    grade: str
    unit: str  # 'pcs', 'kg', 'liters', etc. (no conversion factors)

class ItemCreate(ItemBase):
    id: str

class ItemResponse(BaseModel):
    id: str
    name: str
    type: str
    size: str
    grade: str
    unit: str
    current_stock: int
    
    class Config:
        from_attributes = True

class StockBase(BaseModel):
    item_id: str
    quantity: int

class StockResponse(StockBase):
    last_updated: datetime

    class Config:
        from_attributes = True

class StockMovementBase(BaseModel):
    item_id: str
    movement_type: str
    quantity_change: int
    reference_id: Optional[str] = None
    notes: Optional[str] = None

class StockMovementResponse(StockMovementBase):
    id: int
    before_quantity: Optional[int]
    after_quantity: Optional[int]
    recorded_by: str
    movement_date: datetime

    class Config:
        from_attributes = True
