from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

# ==================== PURCHASE LINE ITEMS ====================
class PurchaseLineItemBase(BaseModel):
    item_id: str
    quantity: int
    unit_price: Decimal

class PurchaseLineItemCreate(PurchaseLineItemBase):
    pass

class PurchaseLineItemResponse(PurchaseLineItemBase):
    id: str
    total_price: Decimal
    
    class Config:
        from_attributes = True

# ==================== PURCHASE ====================
class PurchaseBase(BaseModel):
    supplier_id: str
    due_date: Optional[date] = None

class PurchaseCreate(PurchaseBase):
    bill_number: str
    line_items: List[PurchaseLineItemCreate]
    payment_status: Optional[str] = "pending"
    paid_amount: Optional[Decimal] = 0.00
    notes: Optional[str] = None

class PurchaseUpdate(BaseModel):
    payment_status: Optional[str] = None
    paid_amount: Optional[Decimal] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class PurchaseResponse(PurchaseBase):
    bill_number: str
    total_amount: Decimal
    status: str
    payment_status: str
    paid_amount: Decimal
    created_by: str
    date: datetime
    line_items: List[PurchaseLineItemResponse] = []

    class Config:
        from_attributes = True

# ==================== SALE LINE ITEMS ====================
class SaleLineItemBase(BaseModel):
    item_id: str
    quantity: int
    unit_price: Decimal
    blow_price: Optional[Decimal] = 0.00
    cost_basis: Optional[Decimal] = None

class SaleLineItemCreate(SaleLineItemBase):
    pass

class SaleLineItemResponse(SaleLineItemBase):
    id: str
    total_price: Decimal
    
    class Config:
        from_attributes = True

# ==================== SALE ====================
class SaleBase(BaseModel):
    customer_id: str
    due_date: Optional[date] = None
    payment_method: Optional[str] = "cash"

class SaleCreate(SaleBase):
    bill_number: str
    line_items: List[SaleLineItemCreate]
    payment_status: Optional[str] = "pending"
    paid_amount: Optional[Decimal] = 0.00
    notes: Optional[str] = None

class SaleUpdate(BaseModel):
    payment_status: Optional[str] = None
    paid_amount: Optional[Decimal] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class SaleResponse(SaleBase):
    bill_number: str
    total_price: Decimal
    status: str
    payment_status: str
    paid_amount: Decimal
    editable_by_admin_only: bool
    created_by: str
    date: datetime
    line_items: List[SaleLineItemResponse] = []
    
    class Config:
        from_attributes = True
