from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.item import Stock, Item
from app.models.stock_movement import StockMovement
from app.models.transaction import Purchase, Sale, Blow, Waste, PurchaseLineItem, SaleLineItem
from app.schemas.item import StockResponse, ItemResponse, StockMovementResponse, StockMovementBase

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_all_stocks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all stock items with details"""
    stocks = db.query(Stock).all()
    result = []
    
    for stock in stocks:
        item = db.query(Item).filter(Item.id == stock.item_id).first()
        if item:
            result.append({
                "item_id": stock.item_id,
                "item_name": item.name,
                "item_type": item.type,
                "size": item.size,
                "grade": item.grade,
                "unit": item.unit,
                "quantity": stock.quantity,
                "last_updated": stock.last_updated
            })
    
    return result

@router.post("/movements", response_model=StockMovementResponse, status_code=status.HTTP_201_CREATED)
async def create_stock_movement(
    movement: StockMovementBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new stock movement"""
    # Get current stock
    stock = db.query(Stock).filter(Stock.item_id == movement.item_id).first()
    
    if stock:
        before_qty = stock.quantity
        # Update stock based on movement
        stock.quantity += movement.quantity_change
        after_qty = stock.quantity
    else:
        # If stock doesn't exist, create it (only for positive movements)
        if movement.quantity_change <= 0:
            raise HTTPException(status_code=400, detail="Cannot create negative stock for non-existent item")
        
        before_qty = 0
        stock = Stock(item_id=movement.item_id, quantity=movement.quantity_change)
        db.add(stock)
        after_qty = movement.quantity_change
    
    # Create stock movement record
    db_movement = StockMovement(
        item_id=movement.item_id,
        movement_type=movement.movement_type,
        quantity_change=movement.quantity_change,
        reference_id=movement.reference_id,
        notes=movement.notes,
        before_quantity=before_qty,
        after_quantity=after_qty,
        recorded_by=current_user.id
    )
    
    db.add(db_movement)
    db.commit()
    db.refresh(db_movement)
    
    return db_movement

@router.get("/movements", response_model=List[StockMovementResponse])
async def get_stock_movements(
    item_id: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get stock movement history"""
    query = db.query(StockMovement)
    
    if item_id:
        query = query.filter(StockMovement.item_id == item_id)
    
    movements = query.order_by(StockMovement.movement_date.desc()).offset(skip).limit(limit).all()
    return movements

# stocks.py

@router.get("/items", response_model=List[ItemResponse])
async def get_all_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all items with current stock"""
    print(f"\n📊 GET /stocks/items endpoint called")
    print(f"   user={current_user.username}")
    items = db.query(Item).all()
    print(f"   ✅ Found {len(items)} items in database")
    result = []

    for item in items:
        # Get current stock
        stock = db.query(Stock).filter(Stock.item_id == item.id).first()
        current_stock = stock.quantity if stock else 0

        result.append({
            "id": item.id,
            "name": item.name,
            "type": item.type,
            "size": item.size,
            "grade": item.grade,
            "unit": item.unit,
            "current_stock": current_stock
        })
    
    print(f"   ✅ Returning {len(result)} items to client")
    return result

@router.post("/items/auto-create")
async def auto_create_item(
    item_data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Auto-create or fetch item by name (with optional type/size/grade)
    
    If item exists (case-insensitive), returns existing item.
    If not, creates new item with provided name and defaults for missing fields.
    """
    if not item_data.get("name"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item name is required"
        )
    
    name = item_data["name"].strip()
    item_type = item_data.get("type", "bottle")  # Default to 'bottle' instead of 'generic'
    size = item_data.get("size", "standard")
    grade = item_data.get("grade", "A")
    unit = item_data.get("unit", "pcs")
    
    # Check if item exists (case-insensitive by name)
    existing_item = db.query(Item).filter(
        func.lower(Item.name) == func.lower(name)
    ).first()
    
    if existing_item:
        # Get current stock
        stock = db.query(Stock).filter(Stock.item_id == existing_item.id).first()
        current_stock = stock.quantity if stock else 0
        
        return {
            "message": "Item found",
            "item": {
                "id": existing_item.id,
                "name": existing_item.name,
                "type": existing_item.type,
                "size": existing_item.size,
                "grade": existing_item.grade,
                "unit": existing_item.unit,
                "current_stock": current_stock
            },
            "created": False
        }
    
    # Create new item
    import uuid
    new_item = Item(
        id=str(uuid.uuid4()),
        name=name,
        type=item_type,
        size=size,
        grade=grade,
        unit=unit
    )
    db.add(new_item)
    
    # Create stock entry with 0 quantity
    new_stock = Stock(item_id=new_item.id, quantity=0)
    db.add(new_stock)
    
    db.commit()
    db.refresh(new_item)
    
    # Return as dict to ensure proper serialization
    return {
        "message": "Item created",
        "item": {
            "id": new_item.id,
            "name": new_item.name,
            "type": new_item.type,
            "size": new_item.size,
            "grade": new_item.grade,
            "unit": new_item.unit,
            "current_stock": 0
        },
        "created": True
    }

@router.post("/items", status_code=status.HTTP_201_CREATED)
async def create_item(
    item_data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new item (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create items"
        )
    
    # Check if item ID already exists
    existing = db.query(Item).filter(Item.id == item_data["id"]).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item with this ID already exists"
        )
    
    # Simple unit - no conversion factors (e.g., "pcs", "kg", "liters")
    unit = item_data.get("unit", "pcs")
    
    # Construct full name: "ItemName Size Grade"
    full_name = f"{item_data['name']} {item_data['size']} {item_data['grade']}"
    
    # Create item
    new_item = Item(
        id=item_data["id"],
        name=full_name,
        type=item_data["type"],
        size=item_data["size"],
        grade=item_data["grade"],
        unit=unit
    )
    db.add(new_item)
    
    # Create stock entry with 0 quantity
    new_stock = Stock(item_id=item_data["id"], quantity=0)
    db.add(new_stock)
    
    db.commit()
    db.refresh(new_item)
    
    return {"message": "Item created successfully", "item": new_item}

@router.put("/items/{item_id}")
async def update_item(
    item_id: str,
    item_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing item (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update items"
        )
    
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Update item fields
    if "name" in item_data and "size" in item_data and "grade" in item_data:
        # Construct full name
        item.name = f"{item_data['name']} {item_data['size']} {item_data['grade']}"
    if "type" in item_data:
        item.type = item_data["type"]
    if "size" in item_data:
        item.size = item_data["size"]
    if "grade" in item_data:
        item.grade = item_data["grade"]
    if "unit" in item_data:
        # Store unit directly (e.g., "pcs", "kg", "liters")
        item.unit = item_data["unit"]
    
    db.commit()
    db.refresh(item)
    
    return {"message": "Item updated successfully", "item": item}

@router.delete("/items/{item_id}")
async def delete_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an item (Admin only)
    Safety checks:
    - Block deletion if item used in purchases, sales, blows (from/to), wastes, or stock_movements
    - Remove stock row first to avoid FK issues
    Returns 400 for business rule violations instead of 500.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete items"
        )

    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )

    # Check if item is used in any records
    in_purchase_line = db.query(PurchaseLineItem).filter(PurchaseLineItem.item_id == item_id).first()
    in_sale_line = db.query(SaleLineItem).filter(SaleLineItem.item_id == item_id).first()
    in_blow_from = db.query(Blow).filter(Blow.from_item_id == item_id).first()
    in_blow_to = db.query(Blow).filter(Blow.to_item_id == item_id).first()
    in_waste = db.query(Waste).filter(Waste.item_id == item_id).first()
    in_movements = db.query(StockMovement).filter(StockMovement.item_id == item_id).first()

    if any([in_purchase_line, in_sale_line, in_blow_from, in_blow_to, in_waste, in_movements]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Cannot delete item because it is referenced in transactions, waste, or stock movements. "
                "Please remove related records first."
            ),
        )

    # Proceed with deletion in a try/except to surface DB errors as 400 with message
    try:
        # Delete stock first (if exists)
        stock = db.query(Stock).filter(Stock.item_id == item_id).first()
        if stock:
            db.delete(stock)

        # Delete item
        db.delete(item)
        db.commit()
    except Exception as e:
        db.rollback()
        # Return a user-friendly message instead of raw 500
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete item due to related data or constraints: {str(e)}",
        )

    return {"message": "Item deleted successfully"}


@router.get("/debug/all")
async def get_all_sales_debug(db: Session = Depends(get_db)):
    """Debug: Get all sales with full details"""
    sales = db.query(Sale).order_by(Sale.date.desc()).all()
    return {
        "total_count": len(sales),
        "sales": [
            {
                "bill_number": sale.bill_number,
                "customer_id": sale.customer_id,
                "item_id": sale.item_id,
                "quantity": sale.quantity,
                "unit_price": sale.unit_price,
                "total_price": sale.total_price,
                "date": sale.date.isoformat() if sale.date else None,
                "created_by": sale.created_by
            }
            for sale in sales
        ]
    }