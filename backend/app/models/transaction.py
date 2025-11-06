from sqlalchemy import Column, String, Integer, Numeric, DateTime, Date, ForeignKey, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Purchase(Base):
    __tablename__ = "purchases"

    bill_number = Column(String, primary_key=True, index=True)
    supplier_id = Column(String, ForeignKey("suppliers.id"))
    total_amount = Column(Numeric(12, 2), default=0.00)
    status = Column(String, default="pending")  # 'draft', 'pending', 'paid', 'cancelled'
    payment_status = Column(String, default="pending" , nullable = False)  # 'pending', 'partial', 'paid'
    paid_amount = Column(Numeric(12, 2), default=0.00)
    due_date = Column(Date)
    notes = Column(Text)
    created_by = Column(String, ForeignKey("users.id"))
    date = Column(DateTime(timezone=True))  # Removed server_default so we can set it from due_date
    
    # Relationship to line items
    line_items = relationship("PurchaseLineItem", back_populates="purchase", cascade="all, delete-orphan")

class PurchaseLineItem(Base):
    __tablename__ = "purchase_line_items"
    
    id = Column(String, primary_key=True, index=True)
    bill_number = Column(String, ForeignKey("purchases.bill_number", ondelete="CASCADE"))
    item_id = Column(String, ForeignKey("items.id"))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(12, 2))
    total_price = Column(Numeric(12, 2))
    
    # Relationship back to purchase
    purchase = relationship("Purchase", back_populates="line_items")

class Sale(Base):
    __tablename__ = "sales"

    bill_number = Column(String, primary_key=True, index=True)
    customer_id = Column(String, ForeignKey("customers.id"))
    total_price = Column(Numeric(12, 2), default=0.00)
    status = Column(String, default="confirmed")  # 'draft', 'confirmed', 'shipped', 'paid', 'cancelled'
    payment_status = Column(String, default="pending")  # 'pending', 'partial', 'paid'
    payment_method = Column(String(50), nullable=True, default="cash")
    paid_amount = Column(Numeric(12, 2), default=0.00)
    due_date = Column(Date)
    notes = Column(Text)
    editable_by_admin_only = Column(Boolean, default=False)
    created_by = Column(String, ForeignKey("users.id"))
    date = Column(DateTime(timezone=True))  # Removed server_default so we can set it from due_date
    
    # Relationship to line items
    line_items = relationship("SaleLineItem", back_populates="sale", cascade="all, delete-orphan")

class SaleLineItem(Base):
    __tablename__ = "sale_line_items"
    
    id = Column(String, primary_key=True, index=True)
    bill_number = Column(String, ForeignKey("sales.bill_number", ondelete="CASCADE"))
    item_id = Column(String, ForeignKey("items.id"))
    quantity = Column(Integer)
    unit_price = Column(Numeric(12, 2))
    blow_price = Column(Numeric(12, 2), default=0.00)
    total_price = Column(Numeric(12, 2))
    cost_basis = Column(Numeric(12, 2))
    
    # Relationship back to sale
    sale = relationship("Sale", back_populates="line_items")


class Blow(Base):
    __tablename__ = "blows"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    from_item_id = Column(String, ForeignKey("items.id"))
    to_item_id = Column(String, ForeignKey("items.id"))
    quantity = Column(Integer)
    blow_cost_per_unit = Column(Numeric(12, 2))
    produced_unit_cost = Column(Numeric(12, 2), nullable=True)
    input_quantity = Column(Integer, default=0)
    output_quantity = Column(Integer, default=0)
    waste_quantity = Column(Integer, default=0)
    efficiency_rate = Column(Numeric(5, 2), default=0.00)
    notes = Column(Text)
    date_time = Column(DateTime(timezone=True), server_default=func.now())

class Waste(Base):
    __tablename__ = "wastes"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    item_id = Column(String, ForeignKey("items.id"))
    quantity = Column(Integer)
    price_per_unit = Column(Numeric(12, 2))
    total_price = Column(Numeric(12, 2))
    notes = Column(Text)
    date = Column(DateTime(timezone=True), server_default=func.now())


class ExtraExpenditure(Base):
    __tablename__ = "extra_expenditures"

    id = Column(String, primary_key=True, index=True)
    expense_type = Column(String, nullable=False)  # 'Lunch', 'Electricity', 'Office Supplies', etc.
    description = Column(Text)
    amount = Column(Numeric(12, 2), nullable=False)
    date = Column(Date, nullable=False)
    notes = Column(Text)
    created_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
