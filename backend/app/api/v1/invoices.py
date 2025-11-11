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
from app.utils.invoice_pdf_generator import generate_sales_invoice_pdf
import logging

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
        
        # Generate PDF
        pdf_buffer = generate_sales_invoice_pdf(
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
        
        # Generate PDF
        from app.utils.invoice_pdf_generator import InvoiceReportGenerator
        
        generator = InvoiceReportGenerator()
        
        # Prepare items
        pdf_items = []
        total_amount = 0
        
        for line_item in line_items:
            item = next((i for i in items_list if i.id == line_item.item_id), None)
            item_name = item.name if item else line_item.item_id
            amount = float(line_item.quantity) * float(line_item.unit_price)
            
            pdf_items.append({
                'item_name': item_name,
                'quantity': float(line_item.quantity),
                'unit_price': float(line_item.unit_price),
                'amount': amount,
            })
            total_amount += amount
        
        # Get received amount and payment status
        received_amount = float(purchase.paid_amount) if purchase.paid_amount else 0
        payment_status = purchase.payment_status if hasattr(purchase, 'payment_status') else 'pending'
        
        # Generate PDF
        pdf_buffer = generator.generate_invoice_pdf(
            company_name="Waze Enterprises - Water Bottle Division",
            company_address="Your Company Address",
            company_phone="+92 XXX XXXXXXX",
            company_email="info@waze-enterprises.com",
            invoice_no=purchase.bill_number,
            invoice_date=purchase.date.strftime('%d-%m-%Y') if hasattr(purchase.date, 'strftime') else str(purchase.date),
            bill_to_name=supplier.name if supplier else "Unknown Supplier",
            bill_to_address=supplier.address if supplier and hasattr(supplier, 'address') else "",
            bill_to_contact=supplier.phone if supplier and hasattr(supplier, 'phone') else "",
            items=pdf_items,
            terms="Thank you for doing business with us!",
            signature_line="Authorized Signatory",
            received_amount=received_amount,
            payment_status=payment_status
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
