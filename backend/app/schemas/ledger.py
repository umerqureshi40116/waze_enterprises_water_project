from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import date, datetime


class LedgerEntry(BaseModel):
    """Single transaction entry in ledger"""
    date: date
    reference_number: str
    description: str
    debit: float = 0.00  # Amount owed (for suppliers) or owed to us (for customers)
    credit: float = 0.00  # Amount paid
    balance: float  # Running balance
    payment_status: str  # 'pending', 'partial', 'paid'
    transaction_type: str  # 'purchase', 'sale', 'payment'

    model_config = ConfigDict(from_attributes=True)


class LedgerResponse(BaseModel):
    """Complete ledger response for a customer or supplier"""
    party_id: str
    party_name: str
    party_type: str  # 'customer' or 'supplier'
    month: int
    year: int
    opening_balance: float = 0.00
    closing_balance: float = 0.00
    total_debit: float = 0.00
    total_credit: float = 0.00
    transactions: List[LedgerEntry]

    model_config = ConfigDict(from_attributes=True)


class LedgerSummary(BaseModel):
    """Summary of transactions without full details"""
    party_id: str
    party_name: str
    party_type: str
    total_outstanding: float  # Total amount still owed/owing
    last_transaction_date: Optional[date] = None
    contact: Optional[str] = None
    address: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
