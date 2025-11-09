"""
Initialize database with sample data
Run this script once after database setup
"""
from app.db.database import SessionLocal, init_db
from app.models.user import User
from app.models.party import Supplier, Customer
from app.models.item import Item, Stock
from app.core.security import get_password_hash

def init_sample_data():
    """Initialize database with sample data"""
    db = SessionLocal()
    
    try:
        # Create tables
        print("Creating database tables...")
        init_db()
        
        # Check if data already exists
        existing_user = db.query(User).first()
        if existing_user:
            print("Database already initialized!")
            return
        
        print("Initializing sample data...")
        
        # Users
        users = [
            User(
                id="waheed",
                username="waheed",
                email="waheed@company.com",
                password_hash=get_password_hash("admin123"),
                role="admin"
            ),
            User(
                id="umer",
                username="umer",
                email="umer@company.com",
                password_hash=get_password_hash("user123"),
                role="user"
            )
        ]
        db.add_all(users)
        
        # Suppliers
        suppliers = [
            Supplier(
                id="Supplier_Alpha",
                name="Alpha Plastics",
                contact="0300-1111111",
                address="Karachi",
                notes="Main preform supplier"
            ),
            Supplier(
                id="Supplier_Hydro",
                name="HydroTech Pvt Ltd",
                contact="0301-2222222",
                address="Lahore",
                notes="Blow mold supplier"
            ),
            Supplier(
                id="Supplier_PurePET",
                name="PurePET Traders",
                contact="0321-3333333",
                address="Faisalabad",
                notes="Grade A preform source"
            )
        ]
        db.add_all(suppliers)
        
        # Customers
        customers = [
            Customer(
                id="Customer_Aqua",
                name="Aqua Fresh Pvt Ltd",
                contact="0344-4444444",
                address="Lahore",
                notes="Regular buyer"
            ),
            Customer(
                id="Customer_Crystal",
                name="Crystal Waters",
                contact="0355-5555555",
                address="Karachi",
                notes="Bulk buyer"
            )
        ]
        db.add_all(customers)
        
        # Items
        items = [
            Item(
                id="Item_Preform_500A",
                name="PET Preform 500ml A",
                type="preform",
                size="500ml",
                grade="A",
                unit="pcs (1000)"
            ),
            Item(
                id="Item_Preform_1500A",
                name="PET Preform 1500ml A",
                type="preform",
                size="1500ml",
                grade="A",
                unit="pcs (1000)"
            ),
            Item(
                id="Item_Bottle_500A",
                name="500ml Bottle A",
                type="bottle",
                size="500ml",
                grade="A",
                unit="pcs (1000)"
            ),
            Item(
                id="Item_Bottle_1500A",
                name="1500ml Bottle A",
                type="bottle",
                size="1500ml",
                grade="A",
                unit="pcs (1000)"
            ),
            Item(
                id="Item_Sold_500A",
                name="Sold 500ml Bottle A",
                type="sold",
                size="500ml",
                grade="A",
                unit="pcs (1000)"
            )
        ]
        db.add_all(items)
        
        # Initial Stock
        stocks = [
            Stock(item_id="Item_Preform_500A", quantity=2000),
            Stock(item_id="Item_Preform_1500A", quantity=1000),
            Stock(item_id="Item_Bottle_500A", quantity=800),
            Stock(item_id="Item_Bottle_1500A", quantity=400),
            Stock(item_id="Item_Sold_500A", quantity=0)
        ]
        db.add_all(stocks)
        
        db.commit()
        print("✅ Database initialized successfully!")
        print("\n📝 Sample Login Credentials:")
        print("   Admin: waheed / admin123")
        print("   User:  umer / user123")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_sample_data()
