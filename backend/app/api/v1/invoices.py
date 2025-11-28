"""
Invoice PDF Generation Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.transaction import Sale, Purchase
from app.models.item import Item
from app.models.party import Customer, Supplier
from fastapi.responses import StreamingResponse
from app.utils.invoice_pdf_generator import generate_sales_invoice_pdf, generate_purchase_invoice_pdf
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
            logger.warning(f"Sale not found: {bill_number}")
            raise HTTPException(status_code=404, detail="Sale bill not found")
        
        logger.info(f"Found sale: {bill_number}, date={sale.date}, due_date={sale.due_date}")
        
        # Get customer
        customer = db.query(Customer).filter(Customer.id == sale.customer_id).first()
        if not customer:
            logger.warning(f"Customer not found for sale: {bill_number}")
        
        # Get line items
        from app.models.transaction import SaleLineItem
        line_items = db.query(SaleLineItem).filter(
            SaleLineItem.bill_number == bill_number
        ).all()
        
        if not line_items:
            logger.warning(f"No line items found for sale: {bill_number}")
            raise HTTPException(status_code=404, detail="No line items found for this sale")
        
        logger.info(f"Found {len(line_items)} line items for sale: {bill_number}")
        
        # Get all items
        items_list = db.query(Item).all()
        logger.info(f"Found {len(items_list)} items in database")
        
        # Generate PDF asynchronously to avoid blocking the event loop
        pdf_buffer = await asyncio.to_thread(
            generate_sales_invoice_pdf,
            sale_bill=sale,
            customer=customer,
            line_items=line_items,
            items_db=items_list
        )
        
        logger.info(f"Successfully generated PDF for sale: {bill_number}")
        
        # Return as downloadable file
        filename = f"invoice_{bill_number}_{sale.due_date.strftime('%Y%m%d') if sale.due_date else 'unknown'}.pdf"
        
        return StreamingResponse(
            iter([pdf_buffer.getvalue()]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating sale invoice PDF for {bill_number}: {str(e)}", exc_info=True)
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
            logger.warning(f"Purchase not found: {bill_number}")
            raise HTTPException(status_code=404, detail="Purchase bill not found")
        
        logger.info(f"Found purchase: {bill_number}, date={purchase.date}, due_date={purchase.due_date}")
        
        # Get supplier
        supplier = db.query(Supplier).filter(Supplier.id == purchase.supplier_id).first()
        if not supplier:
            logger.warning(f"Supplier not found for purchase: {bill_number}")
        
        # Get line items
        from app.models.transaction import PurchaseLineItem
        line_items = db.query(PurchaseLineItem).filter(
            PurchaseLineItem.bill_number == bill_number
        ).all()
        
        if not line_items:
            logger.warning(f"No line items found for purchase: {bill_number}")
            raise HTTPException(status_code=404, detail="No line items found for this purchase")
        
        logger.info(f"Found {len(line_items)} line items for purchase: {bill_number}")
        
        # Get all items
        items_list = db.query(Item).all()
        logger.info(f"Found {len(items_list)} items in database")
        
        # Generate PDF asynchronously to avoid blocking the event loop
        pdf_buffer = await asyncio.to_thread(
            generate_purchase_invoice_pdf,
            purchase_bill=purchase,
            supplier=supplier,
            line_items=line_items,
            items_db=items_list
        )
        
        logger.info(f"Successfully generated PDF for purchase: {bill_number}")
        
        # Return as downloadable file
        filename = f"purchase_invoice_{bill_number}_{purchase.due_date.strftime('%Y%m%d') if purchase.due_date else 'unknown'}.pdf"
        
        return StreamingResponse(
            iter([pdf_buffer.getvalue()]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating purchase invoice PDF for {bill_number}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")
