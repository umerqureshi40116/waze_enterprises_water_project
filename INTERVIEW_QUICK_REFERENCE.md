# FastAPI Interview - Quick Reference & Practical Examples

## PART 1: QUICK FACTS ABOUT YOUR PROJECT

### Project Name
**Water Bottle Manufacturing & Inventory Management System**

### Technologies (Stack)
```
Frontend:     React.js (JavaScript)
Backend:      FastAPI (Python)
Database:     PostgreSQL (Cloud: Neon)
Deployment:   Docker, Railway/Render (Backend), Vercel (Frontend)
Authentication: JWT + Bcrypt
```

### Purpose
Track complete lifecycle of water bottle manufacturing from:
- **Raw materials** (preforms) purchased from suppliers
- **Manufacturing** (converting preforms to bottles via blow molding)
- **Finished products** (bottles) sold to customers
- **Financial tracking** (revenue, costs, profit)

### Who Uses It
- Factory owner/manager
- Inventory staff
- Sales staff
- Admin users
(Not for customers/public)

### Key Numbers
- **40-60 API endpoints**
- **10+ database tables**
- **Capacity: 100-500 transactions/day** without issues
- **Scalable to: 1M+ records** with optimization

---

## PART 2: DATABASE SCHEMA QUICK VIEW

```
USERS                          ITEMS
├─ id (UUID)                   ├─ id (String)
├─ username                    ├─ name
├─ email                       ├─ type (preform/bottle/sold)
├─ password_hash               ├─ size (500ml, 1500ml)
└─ role (admin/user)           ├─ grade (A/B/C)
                               └─ unit (pcs, kg, liters)
                                    ↑
                                    │
STOCKS                              │
├─ item_id ─────────────────────────┘
├─ quantity
└─ last_updated

SUPPLIERS                      CUSTOMERS
├─ id                          ├─ id
├─ name                        ├─ name
├─ contact                     ├─ contact
├─ address                     ├─ address
└─ notes                       └─ notes
    ↑                              ↑
    │                              │
PURCHASES                      SALES
├─ bill_number                 ├─ bill_number
├─ supplier_id ─────┘          ├─ customer_id ────┘
├─ total_amount                ├─ total_price
├─ payment_status              ├─ payment_status
├─ date                        ├─ date
└─ created_by                  └─ created_by
    │                              │
    ↓                              ↓
PURCHASE_LINE_ITEMS           SALE_LINE_ITEMS
├─ id                         ├─ id
├─ bill_number                ├─ bill_number
├─ item_id                    ├─ item_id
├─ quantity                   ├─ quantity
├─ unit_price                 ├─ unit_price
└─ total_price                ├─ blow_price
                              └─ total_price

BLOWS (Manufacturing)
├─ id
├─ user_id
├─ from_item_id (preform)
├─ to_item_id (bottle)
├─ quantity
├─ blow_cost_per_unit
└─ produced_unit_cost
```

---

## PART 3: TOP 10 INTERVIEW QUESTIONS & ANSWERS

### Q1: Explain this project in 1 minute
**A:** "This is an inventory management system for a water bottle manufacturing company. Users can:
1. Record purchases from suppliers (buying raw materials)
2. Track manufacturing (converting preforms to bottles)
3. Record sales to customers
4. View inventory levels
5. Generate profit/loss reports

Built with FastAPI backend, PostgreSQL database, React frontend. It scales to handle thousands of transactions daily."

---

### Q2: What are the main features?
**A:**
1. **Inventory Management** - Track stock levels, history
2. **Purchase Management** - Create bills, track supplier orders
3. **Sales Management** - Create invoices, track customer orders
4. **Manufacturing** - Record blow molding process, track efficiency
5. **Financial Reports** - Profit/loss, cost analysis, customer/supplier reports
6. **User Management** - Multiple users, role-based access
7. **Authentication** - Secure login with JWT tokens

---

### Q3: How is data stored?
**A:** "Data is stored in PostgreSQL database on Neon cloud:
- **Items table**: Product definitions (what we make/buy)
- **Stocks table**: Current quantities
- **Purchases table**: Buying transactions
- **Sales table**: Selling transactions
- **Blows table**: Manufacturing records
- **Users table**: Staff accounts
- **Suppliers/Customers tables**: Business contacts

All connected with foreign keys to maintain data integrity."

---

### Q4: How does authentication work?
**A:** "Two-step process:
1. **Login**: User sends username/password → Backend hashes password with bcrypt → Compares with stored hash → If match, creates JWT token → Returns token to frontend

2. **API Requests**: Frontend sends token in Authorization header → Backend verifies token (check signature, expiration) → If valid, process request → Return data

Token expires after 24 hours → Forces re-login."

---

### Q5: How many entries can the system handle?
**A:** "
- **Items**: 50-100 (different sizes/grades of bottles)
- **Users**: 1,000+ (typically 5-20 factory staff)
- **Suppliers/Customers**: 10,000+ (no practical limit)
- **Daily transactions**: 500+ without issues
- **Total records**: Can handle 10M+ with proper indexing

If needed to scale further:
- Add database caching (Redis)
- Implement pagination for reports
- Archive old data (move to separate archive)
- Use read replicas for reporting"

---

### Q6: What's the most complex part?
**A:** "The most complex part is:

1. **Cost Tracking**: When you sell a bottle, system must know:
   - Cost per bottle = (Material cost + Manufacturing cost) / units produced
   - If 1000 preforms cost $2000 and make 950 bottles = $2.11 per bottle
   - When you sell, profit = selling price - $2.11

2. **Inventory Accuracy**: 
   - Physical inventory must match system
   - Handles discrepancies (theft, damage, miscounting)
   - Needs regular audits

3. **Concurrent Transactions**:
   - Multiple staff entering transactions simultaneously
   - Need database locking to prevent conflicts"

---

### Q7: How would you optimize if reports are slow?
**A:** "Four solutions in order of priority:

1. **Caching** (Quick, 5 minutes)
   - Cache report results for 1 hour
   - If user asks same report again within 1 hour, serve from cache
   
2. **Indexing** (Medium, takes 1 hour)
   - Add database indexes on commonly searched columns
   - Makes queries 10-100x faster
   
3. **Pagination** (Medium, takes 2 hours)
   - Show 100 records per page instead of 10,000
   - Let users navigate with next/previous buttons
   
4. **Pre-computation** (Long-term)
   - Calculate reports every night at 2 AM
   - Store results in separate table
   - User gets instant results in morning"

---

### Q8: How would you prevent fraud?
**A:** "Multiple layers:

1. **Authentication**: Only logged-in users can access
2. **Authorization**: Users can only see/modify their own data
3. **Audit Logging**: Every change logged with who/when/what
4. **Approval Workflow**: Large transactions need multiple approvals
5. **Role Separation**: One user can't create AND approve own transaction
6. **Data Validation**: Catch impossible values (negative stock, negative price)
7. **Regular Audits**: Physical inventory reconciliation monthly
8. **Encryption**: Passwords hashed, data encrypted in transit"

---

### Q9: What if the database crashes?
**A:** "Recovery process:

1. **Automatic Backups**: Neon backs up every hour
2. **Point-in-time Recovery**: Can restore to any point in last 30 days
3. **Redundancy**: Data replicated to multiple servers
4. **Disaster Plan**: If Neon fails completely:
   - Switch to backup database (prepared in advance)
   - Restore from latest backup
   - Notify users of potential data loss (at most 1 hour)
5. **Testing**: Practice restores quarterly to ensure they work

Downtime: 15-30 minutes typically. Data loss: minimal (1 hour max)."

---

### Q10: What would you add next?
**A:** "Priority order:

**Next 3 months (High Value)**:
1. Audit logging - Track every change
2. Low stock alerts - Notify when stock is below threshold
3. Export functionality - Download reports as Excel/PDF

**Next 6 months (Nice-to-have)**:
4. Forecasting - Predict future demand
5. Auto-ordering - System suggests purchase orders
6. Mobile app - Access on phone
7. Advanced analytics - Charts, trends, visualizations

**Long-term (Future)**:
8. Machine learning - Predict profits, detect anomalies
9. API for customers - Let customers check inventory online
10. Multi-warehouse - Support multiple factory locations"

---

## PART 4: PRACTICAL CODE EXAMPLES

### Example 1: API Endpoint Structure

```python
# WHAT IT LOOKS LIKE IN FASTAPI

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1", tags=["sales"])

# CREATE SALE ENDPOINT
@router.post("/sales", status_code=201)
def create_sale(
    sale_data: SaleCreate,                    # Input validation with Pydantic
    db: Session = Depends(get_db),           # Get database session
    current_user = Depends(verify_token)     # Verify user is logged in
):
    """
    Create a new sale order
    - Check if customer exists
    - Check if items are in stock
    - Create sale and line items
    - Update inventory
    - Return sale details
    """
    
    # 1. Validate customer exists
    customer = db.query(Customer).filter(
        Customer.id == sale_data.customer_id
    ).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # 2. Validate items exist and check stock
    for item in sale_data.line_items:
        product = db.query(Item).filter(Item.id == item.item_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Item not found: {item.item_id}")
        
        stock = db.query(Stock).filter(Stock.item_id == item.item_id).first()
        if not stock or stock.quantity < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {item.item_id}")
    
    # 3. Create sale record
    new_sale = Sale(
        bill_number=f"SO-{generate_bill_number()}",
        customer_id=sale_data.customer_id,
        total_price=sum(item.quantity * item.unit_price for item in sale_data.line_items),
        created_by=current_user.id,
        date=datetime.now()
    )
    db.add(new_sale)
    db.flush()  # Get the bill_number
    
    # 4. Create line items and update stock
    for item_data in sale_data.line_items:
        line_item = SaleLineItem(
            bill_number=new_sale.bill_number,
            item_id=item_data.item_id,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            total_price=item_data.quantity * item_data.unit_price
        )
        db.add(line_item)
        
        # Update stock
        stock = db.query(Stock).filter(Stock.item_id == item_data.item_id).first()
        stock.quantity -= item_data.quantity
    
    db.commit()
    
    return {
        "bill_number": new_sale.bill_number,
        "customer_id": new_sale.customer_id,
        "total_price": new_sale.total_price,
        "status": "success"
    }
```

**What happens step-by-step:**
1. FastAPI validates input (Pydantic checks types)
2. Dependencies verify user is logged in
3. Function executes business logic
4. Database transactions (all-or-nothing)
5. Returns JSON response

---

### Example 2: Database Model

```python
# HOW DATABASE TABLE IS DEFINED

from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class Sale(Base):
    __tablename__ = "sales"
    
    # Primary Key (unique identifier)
    bill_number = Column(String, primary_key=True, index=True)
    
    # Foreign Keys (links to other tables)
    customer_id = Column(String, ForeignKey("customers.id"))
    created_by = Column(String, ForeignKey("users.id"))
    
    # Data columns
    total_price = Column(Numeric(12, 2), default=0.00)      # Max 9,999,999.99
    status = Column(String, default="confirmed")            # confirmed, shipped, paid, cancelled
    payment_status = Column(String, default="pending")      # pending, partial, paid
    paid_amount = Column(Numeric(12, 2), default=0.00)
    due_date = Column(Date)
    notes = Column(Text)                                    # Can be NULL
    date = Column(DateTime(timezone=True))
    
    # Relationships (how to access related data)
    line_items = relationship(
        "SaleLineItem",
        back_populates="sale",
        cascade="all, delete-orphan"  # Delete line items when sale deleted
    )
    
    # Constraints (rules)
    # - bill_number must be unique
    # - customer_id must exist in customers table
    # - created_by must exist in users table
    # - total_price >= 0
    # - payment_status must be one of: pending, partial, paid
```

**Database Query Examples:**

```python
# GET: Find a specific sale
sale = db.query(Sale).filter(Sale.bill_number == "SO-001").first()

# GET: Find all sales by a customer
sales = db.query(Sale).filter(Sale.customer_id == "CUST-001").all()

# GET: Find unpaid sales
unpaid_sales = db.query(Sale).filter(
    Sale.payment_status != "paid"
).all()

# GET: Get total revenue this month
from sqlalchemy import func
from datetime import datetime, timedelta

this_month = datetime.now().month
total = db.query(func.sum(Sale.total_price)).filter(
    func.extract('month', Sale.date) == this_month
).scalar()

# UPDATE: Mark sale as paid
sale = db.query(Sale).filter(Sale.bill_number == "SO-001").first()
sale.payment_status = "paid"
sale.paid_amount = sale.total_price
db.commit()

# DELETE: Cancel a sale
sale = db.query(Sale).filter(Sale.bill_number == "SO-001").first()
db.delete(sale)
db.commit()
# Note: This also deletes all related line items (cascade delete)
```

---

### Example 3: Authentication Code

```python
# HOW LOGIN WORKS

from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt

router = APIRouter(prefix="/api/v1/auth")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"

# LOGIN ENDPOINT
@router.post("/login")
def login(username: str, password: str, db: Session):
    """
    User login process
    1. Find user by username
    2. Check password
    3. Create JWT token
    4. Return token
    """
    
    # Step 1: Find user
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Step 2: Verify password
    # user.password_hash = "$2b$12$abcdef..." (bcrypt hash)
    # password = "raj123" (what user typed)
    # pwd_context.verify hashes "raj123" and compares with stored hash
    if not pwd_context.verify(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Step 3: Create JWT token
    payload = {
        "sub": user.id,              # Subject (user ID)
        "username": user.username,
        "role": user.role,           # admin or user
        "exp": datetime.utcnow() + timedelta(hours=24)  # Expires in 24 hours
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    # Step 4: Return token
    return {"access_token": token, "token_type": "bearer"}


# PROTECTED ENDPOINT (requires valid token)
def verify_token(authorization: str = Header(...), db: Session = Depends(get_db)):
    """
    Verify JWT token on every protected endpoint
    - Extract token from "Bearer <token>"
    - Verify signature (ensures token wasn't forged)
    - Check expiration
    - Extract user info
    - Return user
    """
    try:
        # Extract token from header
        # Header looks like: "Authorization: Bearer eyJhbG..."
        token = authorization.split(" ")[1]
        
        # Verify and decode token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired, please login again")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# USAGE IN ENDPOINT
@router.get("/me")
def get_current_user(current_user = Depends(verify_token)):
    """
    Get current logged-in user's info
    Requires valid token in Authorization header
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
        "email": current_user.email
    }
```

---

### Example 4: Response Structure

```python
# HOW API RESPONSES ARE STRUCTURED

# SUCCESS RESPONSE
{
    "bill_number": "SO-251223-0026",
    "customer_id": "CUST-001",
    "customer_name": "ABC Grocery",
    "total_price": 700.00,
    "status": "confirmed",
    "payment_status": "pending",
    "line_items": [
        {
            "item_id": "bottle-500ml-a",
            "item_name": "Bottle 500ml Grade A",
            "quantity": 100,
            "unit_price": 4.00,
            "total_price": 400.00
        },
        {
            "item_id": "bottle-1500ml-a",
            "item_name": "Bottle 1500ml Grade A",
            "quantity": 50,
            "unit_price": 6.00,
            "total_price": 300.00
        }
    ],
    "created_at": "2025-12-23T14:30:00Z",
    "created_by": "USER-RAJ"
}

# ERROR RESPONSES

// 400 Bad Request (Invalid input)
{
    "detail": "Insufficient stock",
    "item_id": "bottle-500ml-a",
    "available": 50,
    "requested": 100,
    "shortage": 50
}

// 404 Not Found
{
    "detail": "Customer not found",
    "customer_id": "CUST-999"
}

// 401 Unauthorized (Not logged in)
{
    "detail": "Invalid credentials"
}

// 403 Forbidden (Not authorized)
{
    "detail": "User does not have permission to perform this action"
}

// 422 Unprocessable Entity (Invalid data format)
{
    "detail": [
        {
            "loc": ["body", "quantity"],
            "msg": "ensure this value is greater than 0",
            "type": "value_error.number.not_gt"
        }
    ]
}
```

---

## PART 5: MOCK INTERVIEW CONVERSATION

### Interviewer: Tell me about a challenging situation you faced in this project

**Your Answer:**
"One of the challenging parts was handling concurrent transactions. Imagine two staff members trying to update inventory simultaneously:

1. Staff A checks stock: 500 bottles available
2. Staff B checks stock: 500 bottles available
3. Staff A sells 300 bottles
4. Staff B sells 300 bottles
5. System now shows -100 bottles (impossible!)

The solution is database **transactions**:
- When Staff A starts updating, database locks the stock record
- Staff B's request waits until Staff A is done
- Staff A sells 300 (stock becomes 200)
- Lock is released
- Staff B starts (sees 200 bottles now, can only sell 200)

This prevents inventory going negative and maintains data integrity."

---

### Interviewer: How would you handle a sudden 10x increase in traffic?

**Your Answer:**
"Assuming 10x increase from 100 to 1000 concurrent users, here's the strategy:

**Immediate (Day 1):**
1. Monitor dashboards (CPU, RAM, database connections)
2. Upgrade database size (more RAM, more storage)
3. Add rate limiting (prevent abuse, max 100 requests/minute per user)
4. Enable caching (cache stock levels, reports)

**Short-term (Week 1):**
1. Add more backend servers (load balancer distributes traffic)
2. Implement Redis caching (instant lookups for frequently accessed data)
3. Optimize slow queries (add database indexes)

**Medium-term (Month 1):**
1. Separate reporting (use read replica for reports, don't stress main database)
2. Archive old data (move transactions older than 1 year)
3. Implement pagination (show 100 records per page, not all 10,000)

**Long-term (Months 3-6):**
1. Database sharding (split by region/customer)
2. Microservices (separate services for inventory, sales, reporting)
3. Event-driven architecture (use message queues)

Cost/Capacity:
- Current: $100/month, handles 100 users
- After optimization: $500/month, handles 10,000 users
- With full scaling: $2000+/month, handles 100,000+ users"

---

### Interviewer: What would you do if a customer reported a duplicate charge?

**Your Answer:**
"Investigation process:

1. **Check Audit Log**: See all transactions from this customer
   - When was the charge made?
   - By which staff member?
   - Any duplicate bill numbers?

2. **Verify Transaction**: Check if it's actually a duplicate
   - Two identical sales? (bill_number, amount, date)
   - Or payment recorded twice on one sale?

3. **If Duplicate Sale**:
   - Check if inventory was adjusted twice
   - If yes, stock is wrong → Need to adjust manually
   - If no, stock is correct → Just delete one sale record
   - Refund customer the duplicate amount

4. **If Duplicate Payment Record**:
   - Delete the duplicate payment record
   - Stock is unaffected
   - Refund customer the extra payment

5. **Prevention**:
   - Check who made the duplicate entry (staff member error or system?)
   - Implement idempotency keys (prevent accidental duplicates if request is retried)
   - Add confirmation dialogs before finalizing large transactions
   - Review staff training

6. **Record-keeping**:
   - Document what happened in audit log
   - Note who fixed it and why
   - Update SOP if system is unclear"

---

## PART 6: COMMON FOLLOW-UP QUESTIONS

### Q: How do you handle timezone issues?
**A:** 
"All dates are stored with UTC timezone. When displaying to users:
- Store in database: `2025-12-23 14:30:00 UTC`
- User in India (UTC+5:30): Convert to `2025-12-23 19:60:00 IST`
- User in USA (UTC-5): Convert to `2025-12-23 09:30:00 EST`

In code:
```python
# Store in UTC
sale.date = datetime.now(timezone.utc)

# When displaying, convert to user's timezone
user_tz = pytz.timezone('Asia/Kolkata')
local_date = sale.date.astimezone(user_tz)
```"

---

### Q: What happens if a payment fails?
**A:**
"Payment failure handling:

1. **Record the Failed Attempt**
   - Log transaction attempt (for audit)
   - Don't change inventory (user didn't actually buy)
   - Set payment_status = 'failed'

2. **Notify User**
   - Show error message
   - Suggest retry
   - Provide support contact

3. **Retry Logic**
   - User can retry immediately (funds not locked)
   - System tries payment again
   - If succeeds, update status to 'paid'
   - If fails, show error again

4. **Prevent Duplicate Payments**
   - Use idempotency key (same key = same result)
   - If same payment retried, don't double-charge

5. **Reconciliation**
   - Monthly: Check if payment_status matches actual payments
   - Investigate discrepancies
   - Fix manually if needed"

---

### Q: How do you ensure data privacy?
**A:**
"Multiple layers:

1. **Authentication**: Only authorized users can login
2. **Authorization**: Users can only see their own data
3. **Encryption at Rest**: Database is encrypted (Neon does this)
4. **Encryption in Transit**: HTTPS for all communication
5. **Access Control**: 
   - Admin can see all data
   - User can see only their own transactions
   - View-only users can't modify data
6. **Audit Logging**: Track who accessed what data and when
7. **Data Masking**: Hide sensitive data (passwords, credit cards)
8. **Regular Backups**: Encrypted backups stored separately"

---

### Q: How would you debug a slow query?
**A:**
"Step-by-step debugging:

1. **Identify Slow Query** (using APM tools like Prometheus)
   - Which endpoint is slow?
   - How slow? (1s, 10s, 100s?)
   
2. **Check Query Execution Plan**
   ```sql
   EXPLAIN ANALYZE SELECT * FROM sales WHERE date > '2025-01-01'
   ```
   - Look for 'Seq Scan' (bad, scans entire table)
   - Look for 'Index Scan' (good, uses index)

3. **Add Database Index** (if missing)
   ```sql
   CREATE INDEX idx_sales_date ON sales(date)
   ```
   - Try again, should be 10-100x faster

4. **Check Join Efficiency**
   - If query joins multiple tables, ensure foreign keys are indexed
   - Add composite indexes for common combinations

5. **Review Application Code**
   - N+1 problem: Looping and querying one row at a time
   - Solution: Batch queries or use ORM eager loading

6. **Optimize Data Volume**
   - Pagination (show 100 rows, not 10,000)
   - Caching (cache results for 1 hour)
   - Archival (move old data to separate table)

7. **Monitor and Alert**
   - If query takes > 1s, alert DevOps
   - Track trend (getting slower over time?)
   - Plan optimization before it becomes problem"

---

## PART 7: SALARY DISCUSSION PREPARATION

### What you've built (show confidence)
- ✅ Full-stack application (frontend + backend + database)
- ✅ Production-ready deployment (cloud database, containerized)
- ✅ Authentication & authorization (JWT, bcrypt)
- ✅ Complex business logic (inventory tracking, profit calculation)
- ✅ API with 40-60 endpoints
- ✅ Scalable architecture (can handle growth)

### Skills you've demonstrated
- FastAPI & Python backend
- PostgreSQL & relational databases
- React & JavaScript frontend
- Docker & containerization
- RESTful API design
- Database design & optimization
- Authentication & security
- Scalability planning

### Experience metrics
- "Built complete inventory management system from scratch"
- "Deployed to production environment (Railway, Render, Neon)"
- "Handled multiple concurrent users, implemented transaction management"
- "Optimized database queries, implemented caching strategies"
- "Built authentication system with JWT tokens and bcrypt hashing"

### Realistic salary expectation (India)
- Junior Backend Developer: ₹3.5L - 5.5L (with this project)
- Junior Full-stack Developer: ₹4L - 6.5L
- Experienced candidates: ₹6L - 12L+ (based on experience)

**Negotiation tips:**
- Lead with what you've built (concrete evidence)
- Mention scalability (shows systems thinking)
- Highlight production deployment (shows maturity)
- Reference the full-stack nature (more valuable)

---

**Best of Luck with Your Interview! 🚀**

You have a solid project to talk about. Focus on:
1. Understanding the business problem (inventory tracking)
2. Explaining technical solutions simply
3. Showing you can debug and optimize
4. Demonstrating scalability thinking

