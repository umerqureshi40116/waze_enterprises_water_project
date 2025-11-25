from sqlalchemy import Column, String, Text
from app.db.database import Base

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contact = Column(String)
    address = Column(String)
    notes = Column(Text)

class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contact = Column(String)
    address = Column(String)
    notes = Column(Text)
