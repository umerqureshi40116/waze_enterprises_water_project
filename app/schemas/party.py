from pydantic import BaseModel
from typing import Optional

class SupplierBase(BaseModel):
    name: str
    contact: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None

class SupplierCreate(SupplierBase):
    id: str

class SupplierResponse(SupplierBase):
    id: str

    class Config:
        from_attributes = True

class CustomerBase(BaseModel):
    name: str
    contact: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None

class CustomerCreate(CustomerBase):
    id: str

class CustomerResponse(CustomerBase):
    id: str
    name: str
    class Config:
        from_attributes = True

