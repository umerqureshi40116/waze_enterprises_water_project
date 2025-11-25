from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
from decimal import Decimal

class ExtraExpenditureCreate(BaseModel):
    id: str
    expense_type: str
    description: Optional[str] = None
    amount: Decimal
    date: date
    notes: Optional[str] = None

class ExtraExpenditureUpdate(BaseModel):
    expense_type: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    date: Optional[date] = None
    notes: Optional[str] = None

class ExtraExpenditureResponse(BaseModel):
    id: str
    expense_type: str
    description: Optional[str] = None
    amount: Decimal
    date: date
    notes: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
