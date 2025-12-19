"""
Invoice PDF Generation Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.transaction import Sale, Purchase, Blow, Waste
from app.models.item import Item
from app.models.party import Customer, Supplier
from fastapi.responses import StreamingResponse
from app.utils.invoice_pdf_generator import generate_sales_invoice_pdf, generate_purchase_invoice_pdf, generate_blow_invoice_pdf, generate_waste_invoice_pdf
import logging
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/invoice/sale/{bill_number}")
async def download_sale_invoice(
    bill_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download a professional invoice PDF for a sale bill
    Format: Similar to Care Packages invoice
    """
    try:
        # Get sale bill
        sale = db.query(Sale).filter(Sale.bill_number == bill_number).first()
        if not sale:
            raise HTTPException(status_code=404, detail="Sale bill not found")
        
        # Get customer
        customer = db.query(Customer).filter(Customer.id == sale.customer_id).first()
        
        # Get line items
        from app.models.transaction import SaleLineItem
        line_items = db.query(SaleLineItem).filter(
            SaleLineItem.bill_number == bill_number
        ).all()
        
        if not line_items:
            raise HTTPException(status_code=404, detail="No line items found for this sale")
        
        # Get all items
        items_list = db.query(Item).all()
        
        # Generate PDF asynchronously to avoid blocking the event loop
        pdf_buffer = await asyncio.to_thread(
            generate_sales_invoice_pdf,
            sale_bill=sale,
            customer=customer,
            line_items=line_items,
            items_db=items_list
        )
        
        # Return as downloadable file
        filename = f"invoice_{bill_number}_{sale.date.strftime('%Y%m%d')}.pdf"
        
        return StreamingResponse(
            iter([pdf_buffer.getvalue()]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating invoice PDF: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


@router.get("/invoice/purchase/{bill_number}")
async def download_purchase_invoice(
    bill_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download a professional invoice PDF for a purchase bill
    Format: Similar to Care Packages invoice
    """
    try:
        # Get purchase bill
        purchase = db.query(Purchase).filter(Purchase.bill_number == bill_number).first()
        if not purchase:
            raise HTTPException(status_code=404, detail="Purchase bill not found")
        
        # Get supplier
        supplier = db.query(Supplier).filter(Supplier.id == purchase.supplier_id).first()
        
        # Get line items
        from app.models.transaction import PurchaseLineItem
        line_items = db.query(PurchaseLineItem).filter(
            PurchaseLineItem.bill_number == bill_number
        ).all()
        
        if not line_items:
            raise HTTPException(status_code=404, detail="No line items found for this purchase")
        
        # Get all items
        items_list = db.query(Item).all()
        
        # Generate PDF asynchronously to avoid blocking the event loop
        pdf_buffer = await asyncio.to_thread(
            generate_purchase_invoice_pdf,
            purchase_bill=purchase,
            supplier=supplier,
            line_items=line_items,
            items_db=items_list
        )
        
        # Return as downloadable file
        filename = f"purchase_invoice_{bill_number}_{purchase.date.strftime('%Y%m%d')}.pdf"
        
        return StreamingResponse(
            iter([pdf_buffer.getvalue()]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating purchase invoice PDF: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


@router.get("/invoice/blow/{blow_id}")
async def download_blow_invoice(
    blow_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download a professional invoice PDF for a blow process
    Format: Similar to Sales/Purchase invoices
    """
    try:
        # Get blow record
        blow = db.query(Blow).filter(Blow.id == blow_id).first()
        if not blow:
            raise HTTPException(status_code=404, detail="Blow record not found")
        
        # Get items involved
        from_item = db.query(Item).filter(Item.id == blow.from_item_id).first()
        to_item = db.query(Item).filter(Item.id == blow.to_item_id).first()
        
        if not from_item or not to_item:
            raise HTTPException(status_code=404, detail="Items not found")
        
        # Generate blow process report PDF in a thread
        pdf_buffer = await asyncio.to_thread(
            generate_blow_invoice_pdf,
            blow=blow,
            from_item=from_item,
            to_item=to_item,
            current_user=current_user
        )
        
        filename = f"blow_process_{blow_id}_{blow.date_time.strftime('%Y%m%d') if hasattr(blow, 'date_time') and blow.date_time else 'unknown'}.pdf"
        
        return StreamingResponse(
            iter([pdf_buffer.getvalue()]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating blow invoice PDF: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


@router.get("/invoice/waste/{waste_id}")
async def download_waste_invoice(
    waste_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download waste record as PDF invoice"""
    try:
        # Get waste record
        waste = db.query(Waste).filter(Waste.id == waste_id).first()
        if not waste:
            raise HTTPException(status_code=404, detail="Waste record not found")
        
        # Get item involved
        item = db.query(Item).filter(Item.id == waste.item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Generate waste report PDF in a thread
        pdf_buffer = await asyncio.to_thread(
            generate_waste_invoice_pdf,
            waste=waste,
            item=item
        )
        
        filename = f"waste_record_{waste_id}_{waste.date.strftime('%Y%m%d') if hasattr(waste, 'date') and waste.date else 'unknown'}.pdf"
        
        return StreamingResponse(
            iter([pdf_buffer.getvalue()]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating waste invoice PDF: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")
