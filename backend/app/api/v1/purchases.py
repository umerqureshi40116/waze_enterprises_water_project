from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
from app.db.database import get_db
from app.core.security import get_current_user, get_current_admin_user
from app.models.user import User
from app.models.transaction import Purchase, PurchaseLineItem
from app.models.item import Stock
from app.models.stock_movement import StockMovement
from app.models.party import Supplier
from fastapi import Body
from fastapi.responses import StreamingResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
import os
from datetime import datetime
from app.schemas.transaction import PurchaseCreate, PurchaseUpdate, PurchaseResponse
import logging

router = APIRouter()

@router.post("/", response_model=PurchaseResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase(
    purchase: PurchaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new purchase with multiple line items"""
    logging.info(f"📦 Received purchase request: due_date={purchase.due_date}, type={type(purchase.due_date)}")
    
    # Check if bill number exists
    existing = db.query(Purchase).filter(Purchase.bill_number == purchase.bill_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bill number already exists")
    
    # Validate that at least one line item exists
    if not purchase.line_items or len(purchase.line_items) == 0:
        raise HTTPException(status_code=400, detail="At least one line item is required")
    
    # Calculate total amount and prepare line items data
    total_amount = Decimal('0')
    line_items_data = []
    
    for line_item in purchase.line_items:
        # Calculate line item total: quantity × unit_price
        line_total = Decimal(str(line_item.quantity)) * Decimal(str(line_item.unit_price))
        total_amount += line_total
        
        line_items_data.append({
            'item_id': line_item.item_id,
            'quantity': line_item.quantity,
            'unit_price': Decimal(str(line_item.unit_price)),
            'total_price': line_total
        })
    
    # Create Purchase header record
    # Use due_date as the transaction date (allows user to select custom date)
    purchase_date = None
    if purchase.due_date:
        purchase_date = datetime.combine(purchase.due_date, datetime.min.time())
    else:
        purchase_date = datetime.utcnow()
    
    logging.info(f"📅 Creating purchase with date: {purchase_date}")
    
    db_purchase = Purchase(
        bill_number=purchase.bill_number,
        supplier_id=purchase.supplier_id,
        total_amount=total_amount,
        payment_status=purchase.payment_status if hasattr(purchase, 'payment_status') else 'pending',
        created_by=current_user.id,
        due_date=purchase.due_date,
        date=purchase_date
    )
    db.add(db_purchase)
    db.flush()  # Flush to ensure bill_number is available for foreign key
    
    # Create PurchaseLineItem records and update stock
    for line_data in line_items_data:
        # Generate unique ID for line item
        line_item_id = f"{purchase.bill_number}-{line_data['item_id']}"
        
        # Create line item
        purchase_line_item = PurchaseLineItem(
            id=line_item_id,
            bill_number=purchase.bill_number,
            item_id=line_data['item_id'],
            quantity=line_data['quantity'],
            unit_price=line_data['unit_price'],
            total_price=line_data['total_price']
        )
        db.add(purchase_line_item)
        
        # Update stock
        stock = db.query(Stock).filter(Stock.item_id == line_data['item_id']).first()
        if stock:
            before_qty = stock.quantity
            stock.quantity += line_data['quantity']
            after_qty = stock.quantity
        else:
            before_qty = 0
            stock = Stock(item_id=line_data['item_id'], quantity=line_data['quantity'])
            db.add(stock)
            after_qty = line_data['quantity']
        
        # Record stock movement
        movement = StockMovement(
            item_id=line_data['item_id'],
            movement_type='purchase',
            quantity_change=line_data['quantity'],
            reference_id=purchase.bill_number,
            before_quantity=before_qty,
            after_quantity=after_qty,
            recorded_by=current_user.id,
            notes=f"Purchase from supplier - Line item"
        )
        db.add(movement)
    
    db.commit()
    db.refresh(db_purchase)
    return db_purchase


@router.get("/", response_model=List[PurchaseResponse])
async def get_purchases(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all purchases with line items"""
    try:
        purchases = db.query(Purchase).order_by(Purchase.date.desc()).offset(skip).limit(limit).all()
        
        # Ensure line_items are loaded
        for purchase in purchases:
            if purchase.line_items is None:
                purchase.line_items = []
        
        return purchases
    except Exception as e:
        logging.error(f"Error getting purchases: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Error fetching purchases: {str(e)}")

@router.get("/{bill_number}", response_model=PurchaseResponse)
async def get_purchase(
    bill_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific purchase with line items"""
    purchase = db.query(Purchase).filter(Purchase.bill_number == bill_number).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    return purchase

@router.put("/{bill_number}", response_model=PurchaseResponse)
async def update_purchase(
    bill_number: str,
    purchase_update: PurchaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a purchase - Admin for all fields, Users for payment updates only"""
    purchase = db.query(Purchase).filter(Purchase.bill_number == bill_number).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    
    update_data = purchase_update.dict(exclude_unset=True)
    
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
        if field in ['payment_status']:
            setattr(purchase, field, value)
    
    db.commit()
    db.refresh(purchase)
    return purchase

@router.delete("/{bill_number}")
async def delete_purchase(
    bill_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete a purchase and restore stock (Admin only)"""
    purchase = db.query(Purchase).filter(Purchase.bill_number == bill_number).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    
    # Restore stock for all line items
    line_items = db.query(PurchaseLineItem).filter(PurchaseLineItem.bill_number == bill_number).all()
    for line_item in line_items:
        stock = db.query(Stock).filter(Stock.item_id == line_item.item_id).first()
        if stock:
            stock.quantity -= line_item.quantity
    
    # Delete line items (cascade will handle this, but explicit for clarity)
    db.query(PurchaseLineItem).filter(PurchaseLineItem.bill_number == bill_number).delete()
    
    # Delete purchase
    db.delete(purchase)
    db.commit()
    return {"message": "Purchase deleted successfully and stock restored"}



@router.post("/pdf/purchases")
async def download_multiple_purchases(
    bill_numbers: List[str] = Body(..., embed=True),
    signature_admin: str | None = None,
    signature_ceo: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a combined PDF containing multiple purchase bills."""
    if not bill_numbers:
        raise HTTPException(status_code=400, detail="No bill numbers provided")

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Collect valid purchase records
    records = []
    for bill_no in bill_numbers:
        rec = db.query(Purchase).filter(Purchase.bill_number == bill_no).first()
        if not rec:
            continue
        party = db.query(Supplier).filter(Supplier.id == rec.supplier_id).first()
        party_name = party.name if party else rec.supplier_id
        records.append((rec, party_name, bill_no))

    if not records:
        raise HTTPException(status_code=404, detail="No matching purchases found")

    # Pre-calc grand total (one entry per bill)
    grand_total = 0.0
    for rec, _party, _bill in records:
        try:
            bv = float(getattr(rec, 'total_amount', None) or 0)
        except Exception:
            bv = 0.0
        grand_total += bv

    # layout params
    margin_left = 36
    margin_right = 36
    top_margin = 120
    bottom_margin = 72
    content_x = margin_left
    content_w = width - margin_left - margin_right

    # column widths: Bill#, Supplier, Item, Qty, Unit, Total
    base_col_w = [140, 140, 170, 40, 80, 170]
    scale = content_w / sum(base_col_w)
    col_widths = [w * scale for w in base_col_w]
    col_x = [content_x]
    for w in col_widths:
        col_x.append(col_x[-1] + w)
    col_x[-1] = content_x + content_w

    header_h = 20
    row_h = 28
    usable_height = height - top_margin - bottom_margin
    rows_per_page = max(3, int((usable_height - header_h) // row_h))

    def _draw_page_header(page_num):
        band_h = 72
        c.setFillColor(colors.HexColor('#0b69ff'))
        c.rect(0, height - band_h, width, band_h, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(margin_left, height - 25, "Waze Technologies")
        c.setFont("Helvetica", 10)
        c.drawString(margin_left, height - 41, "Rawat Industrial Area")
        c.drawString(margin_left, height - 55, "03439998954")

        # table header
        y_header = height - top_margin + 8
        c.setFillColor(colors.HexColor('#cfe3ff'))
        c.rect(content_x, y_header - header_h + 4, content_w, header_h, stroke=0, fill=1)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 10)
        titles = ["Bill#", "Supplier", "Item", "Qty", "Unit", "Total"]
        for i, title in enumerate(titles):
            x0 = col_x[i]
            x1 = col_x[i+1] if i+1 < len(col_x) else content_x + content_w
            max_w = x1 - x0 - 8
            txt = title
            while pdfmetrics.stringWidth(txt, "Helvetica-Bold", 10) > max_w and len(txt) > 1:
                txt = txt[:-1]
            if pdfmetrics.stringWidth(title, "Helvetica-Bold", 10) > max_w:
                txt = txt[:-1] + "…"
            c.drawString(x0 + 4, y_header - 14, txt)

        return y_header - header_h

    # rows & pagination
    idx = 0
    page = 1
    total_for_pages = 0.0
    while idx < len(records):
        row_start_y = _draw_page_header(page)
        rows_drawn = 0
        for r in range(rows_per_page):
            if idx >= len(records):
                break
            rec, party_name, bill_no = records[idx]
            y_top = row_start_y - (r * row_h)
            y_text = y_top - (row_h / 2) + 4
            c.setFont("Helvetica", 9)
            c.setFillColor(colors.black)

            # separator
            y_line = y_top - row_h
            c.setStrokeColor(colors.HexColor('#d9e6fb'))
            c.setLineWidth(0.5)
            c.line(margin_left, y_line + 2, width - margin_right, y_line + 2)

            # vertical grid
            c.setStrokeColor(colors.HexColor('#bfcfe8'))
            grid_top = row_start_y + 8
            grid_bottom = y_line + 2
            for xg in col_x:
                c.line(xg, grid_top, xg, grid_bottom)
            c.line(width - margin_right, grid_top, width - margin_right, grid_bottom)

            def fit_and_draw(text, x0, x1, y_pos, align='left'):
                max_w = x1 - x0 - 8
                text = '' if text is None else str(text)
                if pdfmetrics.stringWidth(text, 'Helvetica', 9) <= max_w:
                    if align == 'left':
                        c.drawString(x0 + 4, y_pos, text)
                    else:
                        c.drawRightString(x1 - 6, y_pos, text)
                    return
                t = text
                while t and pdfmetrics.stringWidth(t + '…', 'Helvetica', 9) > max_w:
                    t = t[:-1]
                if align == 'left':
                    c.drawString(x0 + 4, y_pos, t + '…')
                else:
                    c.drawRightString(x1 - 6, y_pos, t + '…')

            # bounds
            cell_bounds = []
            for i, x0 in enumerate(col_x):
                if i + 1 < len(col_x):
                    x1 = col_x[i + 1]
                else:
                    x1 = width - margin_right
                cell_bounds.append((x0, x1))

            fit_and_draw(bill_no, cell_bounds[0][0], cell_bounds[0][1], y_text, 'left')
            fit_and_draw(party_name, cell_bounds[1][0], cell_bounds[1][1], y_text, 'left')
            fit_and_draw(getattr(rec, 'item_id', ''), cell_bounds[2][0], cell_bounds[2][1], y_text, 'left')
            fit_and_draw(str(getattr(rec, 'quantity', '')), cell_bounds[3][0], cell_bounds[3][1], y_text, 'right')
            unit_price_val = float(getattr(rec, 'unit_price', 0) or 0)
            fit_and_draw(f"{unit_price_val:,.2f}", cell_bounds[4][0], cell_bounds[4][1], y_text, 'right')
            try:
                bill_total_val = float(getattr(rec, 'total_amount', None) or 0)
            except Exception:
                bill_total_val = 0.0
            fit_and_draw(f"{bill_total_val:,.2f}", cell_bounds[5][0], cell_bounds[5][1], y_text, 'right')

            total_for_pages += bill_total_val
            idx += 1
            rows_drawn += 1

        # if more pages
        if idx < len(records):
            c.showPage()
            page += 1
            continue
        else:
            y_table_end = row_start_y - (rows_drawn * row_h) - 8
            c.setFont("Helvetica-Bold", 12)
            c.setFillColor(colors.black)
            grand_total_y = y_table_end - 26
            c.drawRightString(width - margin_right, grand_total_y, f"Grand Total: {grand_total:,.2f}")

            sig_w = 120
            sig_h = 48
            extra_gap = 100
            sig_y = grand_total_y - extra_gap - sig_h
            c.setFont("Helvetica", 9)

            admin_x = margin_left
            c.drawString(admin_x, sig_y + sig_h + 8, "Authorized by Waheed")
            if signature_admin and os.path.exists(signature_admin):
                try:
                    c.drawImage(signature_admin, admin_x, sig_y, width=sig_w, height=sig_h, mask='auto')
                except Exception:
                    pass

            ceo_x = width - margin_right - sig_w
            c.drawString(ceo_x, sig_y + sig_h + 8, "Authorized by Zeeshan")
            if signature_ceo and os.path.exists(signature_ceo):
                try:
                    c.drawImage(signature_ceo, ceo_x, sig_y, width=sig_w, height=sig_h, mask='auto')
                except Exception:
                    pass

            break

    c.save()
    buffer.seek(0)
    filename = f"combined-purchases-{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=\"{filename}\""})


@router.post("/fix/paid-amounts")
async def fix_paid_amounts_for_paid_purchases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Fix paid_amount for purchases with payment_status='paid' but paid_amount=0.
    Sets paid_amount equal to total_amount for these records.
    """
    try:
        # Find all purchases with payment_status='paid' and paid_amount=0 or null
        purchases_to_fix = db.query(Purchase).filter(
            Purchase.payment_status == 'paid',
            (Purchase.paid_amount == 0) | (Purchase.paid_amount == None)
        ).all()
        
        count = 0
        for purchase in purchases_to_fix:
            purchase.paid_amount = purchase.total_amount
            count += 1
        
        db.commit()
        
        return {
            "message": f"Fixed {count} purchases",
            "count": count,
            "details": f"Set paid_amount equal to total_amount for {count} paid purchases"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error fixing paid amounts: {str(e)}")
