from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class BlowBase(BaseModel):
    from_item_id: str
    to_item_id: Optional[str] = None
    input_quantity: int
    output_quantity: int
    waste_quantity: int
    blow_cost_per_unit: Decimal
    notes: Optional[str] = None

class BlowCreate(BlowBase):
    id: str

class BlowUpdate(BaseModel):
    output_quantity: Optional[int] = None
    waste_quantity: Optional[int] = None
    blow_cost_per_unit: Optional[Decimal] = None
    notes: Optional[str] = None

class BlowResponse(BlowBase):
    id: str
    user_id: str
    quantity: int
    output_quantity: int
    waste_quantity: int
    efficiency_rate: Decimal
    date_time: datetime

    class Config:
        from_attributes = True

class WasteBase(BaseModel):
    item_id: str
    quantity: int
    price_per_unit: Decimal
    notes: Optional[str] = None

class WasteCreate(WasteBase):
    id: str

class WasteUpdate(BaseModel):
    quantity: Optional[int] = None
    price_per_unit: Optional[Decimal] = None
    notes: Optional[str] = None

class WasteResponse(WasteBase):
    id: str
    user_id: str
    total_price: Decimal
    date: datetime

    class Config:
        from_attributes = True
