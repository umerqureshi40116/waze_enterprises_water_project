from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
from datetime import datetime
from app.db.database import get_db
from app.core.security import get_current_user, get_current_admin_user
from app.models.user import User
from app.models.transaction import Sale, SaleLineItem, Blow, Purchase, PurchaseLineItem
from app.models.item import Stock
from app.models.stock_movement import StockMovement
from app.schemas.transaction import SaleCreate, SaleUpdate, SaleResponse
import logging
from sqlalchemy import func

router = APIRouter()

def calculate_cost_basis(item_id: int, quantity: int, unit_price: Decimal, db: Session, exclude_bill_number: str = None) -> Decimal:
    """
    Auto-calculate cost_basis for a sale item using FIFO (First-In-First-Out).
    Tracks actual inventory consumption from purchases.
    
    Priority:
    1. Produced-item cost from recent Blow (if blow produces this item)
    2. FIFO: Cost based on actual available quantity from oldest purchases
    3. Conservative estimate (60% of unit_price)
    """
    cost_basis = None
    
    # Try to find cost from recent Blow
    try:
        latest_blow = db.query(Blow).filter(
            Blow.to_item_id == item_id
        ).order_by(Blow.date_time.desc()).first()
        
        if latest_blow:
            logging.info(f"🔥 Found Blow for item {item_id}, checking if produced_unit_cost exists...")
            if getattr(latest_blow, 'produced_unit_cost', None) is not None:
                cost_basis = float(latest_blow.produced_unit_cost)
                logging.info(f"✅ Using Blow produced_unit_cost: Rs {cost_basis}")
            else:
                # Get last preform purchase price
                last_preform_purchase = db.query(Purchase).filter(
                    Purchase.item_id == latest_blow.from_item_id
                ).order_by(Purchase.date.desc()).first()
                
                preform_price = None
                if last_preform_purchase and last_preform_purchase.unit_price is not None:
                    preform_price = float(last_preform_purchase.unit_price)
                
                blow_cost_unit = float(getattr(latest_blow, 'blow_cost_per_unit', 0) or 0)
                
                if preform_price is not None:
                    cost_basis = preform_price + blow_cost_unit
                    logging.info(f"✅ Using Blow calculated cost (preform {preform_price} + blow {blow_cost_unit}): Rs {cost_basis}")
    except Exception as e:
        logging.warning(f"Error calculating cost from Blow: {e}")
        cost_basis = None
    
    # Fallback: FIFO (First-In-First-Out) from purchases
    if cost_basis is None:
        logging.info(f"📍 Using FIFO method for item {item_id} (quantity={quantity})")
        try:
            # Get all purchases ordered by date (oldest first)
            purchases = db.query(PurchaseLineItem).filter(
                PurchaseLineItem.item_id == item_id
            ).join(Purchase, Purchase.bill_number == PurchaseLineItem.bill_number).order_by(
                Purchase.date.asc(), Purchase.bill_number.asc()
            ).all()
            
            if not purchases:
                # Allow items with no purchase history - use a default cost basis
                logging.warning(f"⚠️  No purchase history found for item {item_id}, using conservative estimate")
                cost_basis = float(unit_price) * 0.6  # 60% of selling price as conservative estimate
                return cost_basis
            
            # Build purchase queue with remaining quantities
            purchase_queue = []
            for p in purchases:
                purchase_queue.append({
                    'bill_number': p.bill_number,
                    'purchased_qty': p.quantity,
                    'unit_price': float(p.unit_price),
                    'remaining': p.quantity  # Track remaining after all sales
                })
            
            logging.info(f"🛒 Purchase queue for item {item_id}:")
            for pq in purchase_queue:
                logging.info(f"   {pq['bill_number']}: {pq['purchased_qty']} units @ Rs {pq['unit_price']}")
            
            # Get ALL sales ordered by date (oldest first), then by bill_number
            # This determines consumption order
            # Exclude the current sale being calculated if specified
            all_sales_query = db.query(SaleLineItem, Sale.date, Sale.bill_number).filter(
                SaleLineItem.item_id == item_id
            ).join(Sale, Sale.bill_number == SaleLineItem.bill_number)
            
            if exclude_bill_number:
                all_sales_query = all_sales_query.filter(Sale.bill_number != exclude_bill_number)
            
            all_sales = all_sales_query.order_by(
                Sale.date.asc(), Sale.bill_number.asc()
            ).all()
            
            logging.info(f"💰 Sales queue for item {item_id} (consumption order):")
            for s, sdate, sbill in all_sales:
                logging.info(f"   {sbill} (Date: {sdate}): {s.quantity} units")
            
            # Simulate FIFO consumption: each sale consumes from the front of the purchase queue
            for sale_line, sale_date, sale_bill in all_sales:
                units_sold = sale_line.quantity
                logging.info(f"  Processing sale {sale_bill}: {units_sold} units")
                
                # Consume from purchase queue in FIFO order
                remaining = units_sold
                for pq in purchase_queue:
                    if remaining <= 0:
                        break
                    if pq['remaining'] > 0:
                        consumed = min(remaining, pq['remaining'])
                        pq['remaining'] -= consumed
                        remaining -= consumed
                        logging.info(f"    Consumed {consumed} from {pq['bill_number']}, {pq['remaining']} remaining in that batch")
            
            logging.info(f"After all sales consumed, remaining inventory:")
            for pq in purchase_queue:
                logging.info(f"   {pq['bill_number']}: {pq['remaining']} units remaining @ Rs {pq['unit_price']}")
            
            # For THIS sale (the one being calculated), we need to figure out:
            # 1. How many total units have been consumed (including this one)
            # 2. At which position in the FIFO queue does this sale land
            # 3. What cost basis applies
            
            # Rebuild the purchase queue with original quantities
            purchase_queue_for_current = []
            for p in purchases:
                purchase_queue_for_current.append({
                    'bill_number': p.bill_number,
                    'purchased_qty': p.quantity,
                    'unit_price': float(p.unit_price),
                    'remaining': p.quantity
                })
            
            # Now consume all previous sales PLUS this current sale
            all_sales_including_current = all_sales + [(None, None, None)]  # Placeholder for current sale
            
            qty_to_account = 0
            current_sale_position = len(all_sales)  # Current sale is at this position
            
            logging.info(f"📊 Total sales including current: {len(all_sales_including_current) - 1} previous + 1 current = {len(all_sales_including_current)}")
            
            # Consume all previous sales
            for sale_line, sale_date, sale_bill in all_sales:
                qty_to_account += sale_line.quantity
                
            logging.info(f"📦 Previous sales consumed: {qty_to_account} units total")
            logging.info(f"📦 Current sale needs: {quantity} units")
            logging.info(f"📦 Total consumed through this sale: {qty_to_account + quantity} units")
            
            # Now simulate consumption to find which purchases this sale will come from
            remaining_qty_for_current = quantity
            total_cost = Decimal('0')
            
            consumed_by_previous = 0
            for sale_line, _, _ in all_sales:
                consumed_by_previous += sale_line.quantity
            
            logging.info(f"💾 FIFO ALLOCATION FOR CURRENT SALE:")
            logging.info(f"   Consumed by previous sales: {consumed_by_previous} units")
            logging.info(f"   Current sale quantity: {quantity} units")
            logging.info(f"   Current sale starts at unit position: {consumed_by_previous + 1}")
            logging.info(f"   Current sale ends at unit position: {consumed_by_previous + quantity}")
            
            units_allocated = 0
            for pq in purchase_queue_for_current:
                purchase_start = units_allocated
                purchase_end = units_allocated + pq['purchased_qty']
                
                logging.info(f"\n   Checking {pq['bill_number']}: units {purchase_start+1}-{purchase_end} (qty={pq['purchased_qty']} @ Rs {pq['unit_price']})")
                
                if remaining_qty_for_current <= 0:
                    logging.info(f"      → Already allocated enough")
                    units_allocated += pq['purchased_qty']
                    continue
                
                # Skip units consumed by previous sales
                if purchase_end <= consumed_by_previous:
                    logging.info(f"      → Fully consumed by previous sales, skip")
                    units_allocated += pq['purchased_qty']
                    continue
                
                # How many units from THIS purchase go to current sale?
                start_in_this_purchase = max(0, consumed_by_previous - units_allocated)
                available_in_this_purchase = pq['purchased_qty'] - start_in_this_purchase
                qty_from_this = min(remaining_qty_for_current, available_in_this_purchase)
                
                cost = qty_from_this * Decimal(str(pq['unit_price']))
                total_cost += cost
                remaining_qty_for_current -= qty_from_this
                
                logging.info(f"      → Allocated {qty_from_this} units (start_offset={start_in_this_purchase}, available={available_in_this_purchase})")
                logging.info(f"      → Cost: {qty_from_this} × Rs {pq['unit_price']} = Rs {cost}")
                
                units_allocated += pq['purchased_qty']
            
            if remaining_qty_for_current > 0:
                # Allow negative stock - use conservative estimate for remaining quantity
                logging.warning(f"⚠️  Insufficient inventory: need {quantity} but only {quantity - remaining_qty_for_current} available. Using conservative estimate for remaining {remaining_qty_for_current} units")
                shortage_cost = Decimal(str(remaining_qty_for_current)) * Decimal(str(unit_price)) * Decimal('0.6')
                total_cost += shortage_cost
            
            cost_basis = float(total_cost / quantity)
            logging.info(f"✅ FINAL: Cost basis = Rs {total_cost} / {quantity} = Rs {cost_basis} per unit")
                
        except Exception as e:
            logging.error(f"❌ Error calculating FIFO cost: {e}", exc_info=True)
            raise HTTPException(status_code=400, detail=f"Cannot calculate cost for item {item_id}: {str(e)}")
    
    return cost_basis


@router.post("/", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
async def create_sale(
    sale: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new sale with multiple line items"""
    # Check if bill number exists
    existing = db.query(Sale).filter(Sale.bill_number == sale.bill_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bill number already exists")
    
    # Validate that at least one line item exists
    if not sale.line_items or len(sale.line_items) == 0:
        raise HTTPException(status_code=400, detail="At least one line item is required")
    
    # Calculate total price and validate stock for all items
    total_price = Decimal('0')
    line_items_data = []
    
    for line_item in sale.line_items:
        # Lock stock for update (prevents race conditions)
        stock = db.query(Stock).filter(
            Stock.item_id == line_item.item_id
        ).with_for_update().first()
        
        if not stock:
            raise HTTPException(
                status_code=400, 
                detail=f"Item {line_item.item_id} not found in stock"
            )
        
        # Calculate line item total: quantity × (unit_price + blow_price)
        blow_price = Decimal(str(line_item.blow_price)) if line_item.blow_price else Decimal('0')
        line_total = Decimal(str(line_item.quantity)) * (Decimal(str(line_item.unit_price)) + blow_price)
        total_price += line_total
        
        # Calculate cost basis
        cost_basis = calculate_cost_basis(
            line_item.item_id,
            line_item.quantity,
            Decimal(str(line_item.unit_price)), 
            db
        )
        
        line_items_data.append({
            'stock': stock,
            'item_id': line_item.item_id,
            'quantity': line_item.quantity,
            'unit_price': Decimal(str(line_item.unit_price)),
            'blow_price': blow_price,
            'total_price': line_total,
            'cost_basis': cost_basis
        })
    
    # Create Sale header record
    # Use due_date as the transaction date (allows user to select custom date)
    sale_date = None
    if sale.due_date:
        sale_date = datetime.combine(sale.due_date, datetime.min.time())
    else:
        sale_date = datetime.utcnow()
    
    logging.info(f"📅 Creating sale with date: {sale_date}")
    
    db_sale = Sale(
        bill_number=sale.bill_number,
        customer_id=sale.customer_id,
        total_price=total_price,
        payment_status=sale.payment_status if hasattr(sale, 'payment_status') else 'pending',
        payment_method=sale.payment_method if hasattr(sale, 'payment_method') else None,
        created_by=current_user.id,
        due_date=sale.due_date,
        date=sale_date
    )
    db.add(db_sale)
    db.flush()  # Flush to ensure bill_number is available for foreign key
    
    # Create SaleLineItem records and update stock
    for line_data in line_items_data:
        # Generate unique ID for line item
        line_item_id = f"{sale.bill_number}-{line_data['item_id']}"
        
        logging.info(f"💾 Storing SaleLineItem: bill={sale.bill_number}, item={line_data['item_id']}, qty={line_data['quantity']}, cost_basis={line_data['cost_basis']}, COGS will be: {line_data['quantity']} × {line_data['cost_basis']} = {line_data['quantity'] * line_data['cost_basis']}")
        
        # Create line item
        sale_line_item = SaleLineItem(
            id=line_item_id,
            bill_number=sale.bill_number,
            item_id=line_data['item_id'],
            quantity=line_data['quantity'],
            unit_price=line_data['unit_price'],
            blow_price=line_data['blow_price'],
            total_price=line_data['total_price'],
            cost_basis=line_data['cost_basis']
        )
        db.add(sale_line_item)
        
        # Update stock
        stock = line_data['stock']
        before_qty = stock.quantity
        stock.quantity -= line_data['quantity']
        after_qty = stock.quantity
        
        # Record stock movement
        movement = StockMovement(
            item_id=line_data['item_id'],
            movement_type='sale',
            quantity_change=-line_data['quantity'],
            reference_id=sale.bill_number,
            before_quantity=before_qty,
            after_quantity=after_qty,
            recorded_by=current_user.id,
            notes=f"Sale to customer - Line item"
        )
        db.add(movement)
    
    db.commit()
    db.refresh(db_sale)
    return db_sale


@router.get("/", response_model=List[SaleResponse])
async def get_sales(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all sales with line items"""
    sales = db.query(Sale).order_by(Sale.date.desc()).offset(skip).limit(limit).all()
    return sales

@router.post("/recalculate-cogs")
async def recalculate_cogs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Recalculate COGS for all sales based on FIFO method"""
    try:
        logging.info("🔄 Starting COGS recalculation for all sales...")
        
        # Get all sales ordered by date, then bill_number
        sales = db.query(Sale).order_by(Sale.date.asc(), Sale.bill_number.asc()).all()
        
        logging.info(f"📊 Processing {len(sales)} sales in order:")
        for sale in sales:
            logging.info(f"   {sale.bill_number} (Date: {sale.date})")
        
        items_updated = 0
        
        for sale in sales:
            for line_item in sale.line_items:
                logging.info(f"\n🔄 Recalculating {sale.bill_number}-{line_item.item_id} (qty={line_item.quantity}, current cost_basis={line_item.cost_basis})")
                
                # Recalculate cost_basis for this line item, excluding this sale from the calculation
                new_cost_basis = calculate_cost_basis(
                    line_item.item_id,
                    line_item.quantity,
                    Decimal(str(line_item.unit_price)),
                    db,
                    exclude_bill_number=sale.bill_number  # Exclude current sale from FIFO queue
                )
                
                old_cost_basis = line_item.cost_basis
                if old_cost_basis != new_cost_basis:
                    logging.info(f"✅ UPDATED: cost_basis {old_cost_basis} → {new_cost_basis}, COGS: {old_cost_basis * line_item.quantity} → {new_cost_basis * line_item.quantity}")
                    line_item.cost_basis = new_cost_basis
                    items_updated += 1
                else:
                    logging.info(f"⏭️  NO CHANGE: cost_basis remains {old_cost_basis}")
        
        db.commit()
        
        logging.info(f"✅ COGS recalculation complete. Updated {items_updated} line items.")
        
        return {
            "status": "success",
            "message": f"Recalculated COGS for {items_updated} line items",
            "items_updated": items_updated
        }
    except Exception as e:
        logging.error(f"Error recalculating COGS: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error recalculating COGS: {str(e)}")

@router.get("/{bill_number}", response_model=SaleResponse)
async def get_sale(
    bill_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific sale with line items"""
    sale = db.query(Sale).filter(Sale.bill_number == bill_number).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale

@router.put("/{bill_number}", response_model=SaleResponse)
async def update_sale(
    bill_number: str,
    sale_update: SaleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a sale - Admin for all fields, Users for payment updates only"""
    sale = db.query(Sale).filter(Sale.bill_number == bill_number).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    update_data = sale_update.dict(exclude_unset=True)
    
    # Non-admin users can only update payment fields
    if current_user.role != 'admin':
        allowed_fields = {'payment_status'}
        if not set(update_data.keys()).issubset(allowed_fields):
            raise HTTPException(
                status_code=403, 
                detail="Only admin can update non-payment fields"
            )
    
    # Update allowed fields
    for field, value in update_data.items():
        if field in ['payment_status', 'payment_method']:
            setattr(sale, field, value)
    
    db.commit()
    db.refresh(sale)
    return sale

@router.delete("/{bill_number}")
async def delete_sale(
    bill_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete a sale and restore stock (Admin only)"""
    sale = db.query(Sale).filter(Sale.bill_number == bill_number).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    # Restore stock for all line items
    line_items = db.query(SaleLineItem).filter(SaleLineItem.bill_number == bill_number).all()
    for line_item in line_items:
        stock = db.query(Stock).filter(Stock.item_id == line_item.item_id).first()
        if stock:
            stock.quantity += line_item.quantity
    
    # Delete line items (cascade will handle this, but explicit for clarity)
    db.query(SaleLineItem).filter(SaleLineItem.bill_number == bill_number).delete()
    
    # Delete sale
    db.delete(sale)
    db.commit()
    return {"message": "Sale deleted successfully and stock restored"}

