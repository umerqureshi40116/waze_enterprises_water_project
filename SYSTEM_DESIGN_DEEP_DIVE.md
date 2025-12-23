# System Design Deep Dive - Interview Ready

## QUESTION: How many entries can be added to this system?

### The Complete Answer:

#### 1. ITEMS (Products)
```
Theoretical limit: UNLIMITED (database can store any amount)
Practical limit: 10,000 - 100,000
Typical for this business: 20-100 items

Why the practical limit?
- Users need to see items in dropdowns (can't show 1M items)
- Need to search/filter items (slower with more items)
- Database queries on items need to be fast
- Staff training (remember item codes/names)

For water bottles specifically:
- Preforms: 5 sizes × 3 grades = 15 items
- Bottles: 5 sizes × 3 grades = 15 items
- Total: ~30-50 items

Example:
- Item: Preform-500ml-A
- Item: Bottle-500ml-A
- Item: Bottle-500ml-B
- Item: Bottle-1500ml-A
... etc
```

#### 2. INVENTORY RECORDS (Stock Transactions)
```
Theoretical limit: UNLIMITED
Practical limit before optimization: 1 million
Practical limit with optimization: 100 million+

What counts as an entry?
- Each PURCHASE is one entry
- Each SALE is one entry
- Each BLOW (manufacturing) is one entry
- Each WASTE is one entry
- Each stock movement is one entry

Typical daily volume: 100-500 entries
Monthly: 3,000-15,000 entries
Yearly: 36,000-180,000 entries

If business grows:
- Year 1-2: 36K-180K entries (easy, no issues)
- Year 3-5: 180K-900K entries (still fine)
- Year 5+: 1M+ entries (need optimization)

Optimization for large datasets:
1. Add database INDEXES on:
   - item_id (search by item)
   - date (search by date range)
   - status (filter by pending/paid)
   
2. PARTITION data by date:
   - Current data (last 90 days)
   - Active data (last 2 years)
   - Archive data (older than 2 years)

3. PAGINATION in reports:
   - Don't load all 1M records
   - Load 100 at a time, show previous/next buttons

4. Caching for repeated queries:
   - Cache stock totals (update every hour)
   - Cache monthly summaries (calculated once)
```

#### 3. USERS (Employees)
```
Theoretical limit: UNLIMITED
Practical limit: 1,000 users
Typical for this business: 5-50 users

Why not more?
- Operational (can't manage 1000 factory workers in this system)
- This is for inventory managers, not every employee
- Would need separate HR system

Breakdown for small factory:
- Owner: 1
- Managers: 2-3
- Inventory staff: 2-3
- Sales staff: 2-3
- Admin: 1
Total: 8-11 users

With 1000 users:
- Still works fine technically
- Just one more table in database
- No performance impact
```

#### 4. SUPPLIERS (Vendor Database)
```
Typical range: 10-200 suppliers
Practical limit: 10,000+

Example:
- Supplier 1: Preform manufacturer
- Supplier 2: Raw material provider
- Supplier 3: Equipment supplier
- Supplier 4: Packaging supplier

Each supplier can have unlimited purchase orders.
```

#### 5. CUSTOMERS (Buyer Database)
```
Typical range: 50-500 customers
Practical limit: 50,000+

Example:
- Customer 1: Retail chain
- Customer 2: Wholesale distributor
- Customer 3: Local grocery store
- Customer 4: Vending machine company

Each customer can make unlimited purchases.
```

#### 6. PURCHASE ORDERS / SALES ORDERS
```
Maximum manageable per month: 10,000+
Theoretical limit: UNLIMITED (with optimization)

Breakdown:
- Small business (month 1-12):
  - Purchases: 10-50/month
  - Sales: 20-100/month
  - Total: 30-150/month

- Growing business (year 2):
  - Purchases: 50-200/month
  - Sales: 100-500/month
  - Total: 150-700/month

- Large business (year 5+):
  - Purchases: 200-1000/month
  - Sales: 500-5000/month
  - Total: 700-6000/month

Each order can have multiple line items (1-100 items per bill typically).
So if 1000 orders with average 5 items = 5000 line items.

Optimization needed at: 10,000+ orders/month
Solution: Archive old orders, use reporting database for queries
```

---

## QUESTION: What's the current capacity and bottlenecks?

### Current Capacity

#### SCENARIO 1: Small Startup (First Year)
```
Daily transactions: 50-100
Monthly transactions: 1,500-3,000
Users: 5-10
Database size: ~100 MB
Typical response time: 50-100ms
Server load: <10% CPU, <500MB RAM
Status: ✅ EXCELLENT - No issues expected
```

#### SCENARIO 2: Growing Company (2-3 Years)
```
Daily transactions: 300-500
Monthly transactions: 9,000-15,000
Users: 15-30
Database size: ~500 MB - 1 GB
Typical response time: 100-200ms
Complex reports: 1-2 seconds
Server load: 20-40% CPU, 1-2 GB RAM
Status: ✅ GOOD - Still very manageable
```

#### SCENARIO 3: Mature Business (5+ Years)
```
Daily transactions: 1,000-5,000
Monthly transactions: 30,000-150,000
Users: 30-100
Database size: 2-10 GB
Typical response time: 200-500ms
Complex reports: 5-30 seconds
Server load: 50-70% CPU, 2-4 GB RAM
Status: ⚠️ MONITOR - Optimization recommended
Actions: Add indexes, implement caching, archive old data
```

#### SCENARIO 4: Large Enterprise (10+ Years)
```
Daily transactions: 5,000-50,000
Monthly transactions: 150,000-1,500,000
Users: 100-500
Database size: 10-100 GB
Typical response time: 500ms-2s
Complex reports: 30-120 seconds
Server load: 70-90% CPU, 4-8 GB RAM
Status: ⚠️ CRITICAL - Major optimization needed
Actions:
  1. Partition database by date
  2. Archive data older than 2 years
  3. Use separate reporting database (read replica)
  4. Implement caching layer (Redis)
  5. Pre-compute common reports nightly
  6. Scale to multiple servers (load balancer)
```

### Current Bottlenecks

#### 1. Report Generation for Large Datasets
**Problem:** Computing profit report for all 10,000 transactions takes 10 seconds

**Why?**
- Database needs to scan all records
- Calculate sums, grouping, aggregations
- Sort results
- Network overhead

**Solutions:**
```
Option 1: Caching (Easiest)
- Cache results for 1 hour
- If user asks again within 1 hour, serve from cache
- Drawback: Data is 1 hour old

Option 2: Pre-computation (Better)
- Calculate reports every night at 2 AM
- Store pre-calculated results in "reports" table
- User gets instant results in morning
- Drawback: Stale data if something happens during day

Option 3: Pagination (for viewing)
- Show 100 records per page instead of 10,000
- Let users navigate with previous/next buttons
- Drawback: Still need to see summary

Option 4: Indexing (Medium-term)
- Add database indexes on frequently searched columns
- Makes queries 10-100x faster
- Requires database optimization
```

#### 2. Stock Lookup Speed
**Problem:** Checking stock of one item takes 50ms (feels slow at scale)

**Why?**
- Database scans stocks table
- Network latency
- Database processing time

**Solutions:**
```
Option 1: Caching (Quick)
- Cache stock values for 5 minutes
- Slight staleness but much faster

Option 2: In-memory cache (Redis)
- Keep latest stock in Redis (cache)
- Update when transaction happens
- Instant lookup (microseconds)

Option 3: Denormalization (Complex)
- Store stock in multiple places
- Trade consistency for speed
- Need careful synchronization
```

#### 3. Concurrent User Limitations
**Problem:** 10 staff entering data simultaneously = conflicts

**Why?**
- Database locks when updating same record
- Users wait for each other
- Can cause conflicts

**Solutions:**
```
Option 1: Database locks (current)
- SQLAlchemy handles this automatically
- First user updates, others wait and retry
- Works fine for 5-20 users

Option 2: Optimistic locking
- Add version number to records
- If version changed, someone else updated
- Merge changes intelligently
- Better for high concurrency

Option 3: Event sourcing
- Store every change as an event
- Build state from events
- Multiple users can work simultaneously
- Complex but very scalable
```

#### 4. Data Growth Over Time
**Problem:** After 5 years, database is 10GB, queries slow

**Why?**
- Scanning 10 million records takes time
- Indexes take space
- Need to read more data from disk

**Solutions:**
```
Option 1: Archival (Best)
- Move transactions older than 2 years to archive
- Keep current 2 years active
- Archive still queryable but slower
- Reduces main database to 2-3 GB

Option 2: Partitioning (Complex but Powerful)
- Split data by year (2023 data, 2024 data, 2025 data)
- Queries automatically use right partition
- Fast queries on recent data
- Can delete old partitions entirely

Option 3: Sharding (Enterprise)
- Split data by customer/supplier
- Each shard on different server
- Very fast queries on smaller datasets
- Complex to implement
```

---

## QUESTION: What's the technical architecture?

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER BROWSERS                         │
│              (Running React Frontend)                    │
└─────────────────────────────────────────────────────────┘
                          ↓
                    HTTPS Requests
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   LOAD BALANCER                          │
│         (Distributes traffic to backends)               │
└─────────────────────────────────────────────────────────┘
                          ↓
         ┌────────────────┼────────────────┐
         ↓                ↓                ↓
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│ Backend #1     │ │ Backend #2     │ │ Backend #3     │
│ FastAPI        │ │ FastAPI        │ │ FastAPI        │
│ (Railway)      │ │ (Railway)      │ │ (Railway)      │
└────────────────┘ └────────────────┘ └────────────────┘
         │                │                │
         └────────────────┼────────────────┘
                          ↓
              ┌──────────────────────┐
              │  Database Connection │
              │    Pool (10-20       │
              │    connections)      │
              └──────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              PostgreSQL Database                        │
│                (Neon Cloud)                            │
│  - Automatic backups every hour                        │
│  - Replication for redundancy                         │
│  - Point-in-time recovery                             │
└─────────────────────────────────────────────────────────┘
```

### Component Breakdown

#### Frontend (React.js)
```
Files in: frontend/src/

Structure:
├── pages/           (Full page components)
│   ├── BlowProcess.jsx    (Record manufacturing)
│   ├── Sales.jsx          (Record sales)
│   ├── Purchases.jsx      (Record purchases)
│   └── Dashboard.jsx      (Overview page)
├── components/      (Reusable components)
│   ├── Header.jsx
│   ├── Sidebar.jsx
│   └── DataTable.jsx
├── api/            (API call functions)
│   ├── itemAPI.js
│   ├── saleAPI.js
│   └── reportAPI.js
└── context/        (State management)
    └── AuthContext.js (Login state)

What it does:
1. User opens browser → React loads
2. User enters credentials
3. React calls API to verify
4. If valid, React calls other APIs (get items, stocks, etc.)
5. React displays data in nice format
6. User submits form → React sends to API
7. API updates database → React shows confirmation

Key concept: Frontend is "stateless"
- Doesn't store data permanently
- All data comes from backend
- If user refreshes page, data reloads from API
```

#### Backend (FastAPI)
```
Files in: backend/app/

Structure:
├── main.py              (Entry point, configure app)
├── core/
│   └── config.py        (Settings, environment variables)
├── db/
│   └── database.py      (Database connection setup)
├── models/              (Database table definitions)
│   ├── item.py          (Items table)
│   ├── user.py          (Users table)
│   ├── transaction.py   (Purchases, Sales, Blows, etc.)
│   └── party.py         (Suppliers, Customers)
├── schemas/             (Data validation)
│   └── *.py             (Pydantic models)
├── api/v1/              (API endpoints)
│   ├── auth.py          (Login, logout)
│   ├── items.py         (Item CRUD)
│   ├── purchases.py     (Purchase CRUD)
│   ├── sales.py         (Sales CRUD)
│   ├── blows.py         (Manufacturing)
│   └── reports.py       (Report generation)
└── utils/               (Helper functions)
    └── *.py

What it does:
1. Receives HTTP request from frontend
2. Validates data (Pydantic schemas)
3. Checks authentication (JWT token)
4. Checks authorization (user role)
5. Executes business logic
6. Queries/updates database (SQLAlchemy ORM)
7. Returns JSON response

Example flow:
POST /api/sales
  Input: {item_id: "bottle-500ml", qty: 100, price: 400}
  → Validate (is qty > 0? is price > 0?)
  → Check auth (is user logged in? is user authorized?)
  → Check stock (do we have 100 bottles?)
  → Create sale record
  → Update stock (-100)
  → Calculate profit
  → Return: {sale_id: "SO-001", profit: 200, status: "success"}
```

#### Database (PostgreSQL)
```
Server: Neon (cloud service)

Tables:
1. users               (Staff accounts)
2. items              (Product definitions)
3. stocks             (Current quantities)
4. suppliers          (Vendors)
5. customers          (Buyers)
6. purchases          (Purchase orders)
7. purchase_line_items (Details of purchases)
8. sales              (Sales orders)
9. sale_line_items    (Details of sales)
10. blows             (Manufacturing records)
11. wastes            (Defects/damages)

Relationships:
- User → Can create multiple Purchases/Sales
- Supplier → Can have multiple Purchases
- Customer → Can have multiple Sales
- Purchase → Can have multiple LineItems
- Sale → Can have multiple LineItems
- Item → Can appear in many Purchases/Sales/Blows

Constraints:
- Primary keys (unique IDs)
- Foreign keys (prevent orphaned records)
- Unique constraints (no duplicate usernames)
- Not null constraints (required fields)
- Check constraints (qty >= 0, price > 0)

Indexes (for speed):
- (user_id) - Fast lookup of user's transactions
- (item_id) - Fast lookup of item's movements
- (date) - Fast lookup by date range
- (status) - Fast lookup by status (pending/paid)
```

---

## QUESTION: How does authentication work?

### Authentication Flow

```
STEP 1: User Login
┌──────────────────────────────────────────┐
│ Browser (React)                          │
│ User enters: username="raj", pwd="123"   │
└──────────────────────────────────────────┘
                    ↓
        Frontend sends POST request:
        POST /api/auth/login
        Body: {username: "raj", password: "123"}
                    ↓
┌──────────────────────────────────────────┐
│ Backend (FastAPI)                        │
│ 1. Find user "raj" in database           │
│ 2. Get stored hash of correct password   │
│ 3. Hash received password "123"          │
│ 4. Compare hashes                        │
│    Received hash == Stored hash?         │
│    YES → Success!                        │
│    NO → Fail, return 401                 │
│ 5. Create JWT token with user info       │
│ 6. Return token to frontend              │
└──────────────────────────────────────────┘
                    ↓
Response: {access_token: "eyJhbG....", token_type: "bearer"}
                    ↓
┌──────────────────────────────────────────┐
│ Browser (React)                          │
│ Saves token in localStorage              │
│ (Stores it locally in browser)           │
└──────────────────────────────────────────┘

STEP 2: User Makes API Request
┌──────────────────────────────────────────┐
│ Browser (React)                          │
│ User clicks "View Sales"                 │
│ React loads token from localStorage      │
│ Sends: GET /api/sales                    │
│        Header: Authorization: "Bearer eyJhbG...."
└──────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────┐
│ Backend (FastAPI)                        │
│ Middleware intercepts request            │
│ 1. Extract token from header             │
│ 2. Decode token (verify signature)       │
│ 3. Check if expired (token valid 24hrs)  │
│ 4. Extract user info from token          │
│ 5. Check if user has permission          │
│    - Admin can see all sales             │
│    - Regular user can see own sales      │
│ 6. If all good, process request          │
│ 7. Return sales data                     │
└──────────────────────────────────────────┘
                    ↓
Response: [{bill: "SO-001", amount: 400}, ...]
                    ↓
┌──────────────────────────────────────────┐
│ Browser (React)                          │
│ Displays sales in table                  │
└──────────────────────────────────────────┘

STEP 3: Token Expires
After 24 hours, token stops working.
User must login again to get new token.
```

### Why This Design?

```
JWT Token Advantages:
✅ Stateless - Backend doesn't need to remember logged-in users
✅ Scalable - Works with multiple servers (no session sharing needed)
✅ Secure - Token is signed, can't be forged
✅ Portable - Can use across multiple services
✅ Self-contained - Token has user info inside it

Bcrypt Advantages:
✅ Slow - Takes 0.1-0.5 seconds per password (makes brute force hard)
✅ Salted - Each password has unique salt (prevents rainbow tables)
✅ Irreversible - Can't get password from hash (even with DB breach)
✅ Industry standard - Used by major companies (Google, Facebook)
```

---

## QUESTION: How does data flow through a transaction?

### Example: Creating a Sales Order

```
STEP 1: User Input (Frontend)
┌─────────────────────────────────────┐
│ User fills form:                    │
│ Customer: ABC Grocery               │
│ Item 1: Bottle-500ml, Qty: 100, @$4 │
│ Item 2: Bottle-1500ml, Qty: 50, @$6 │
│ Due date: 2025-12-30                │
│ Notes: Fast delivery needed         │
│ Clicks: SUBMIT                      │
└─────────────────────────────────────┘
                  ↓
STEP 2: Validation (Frontend)
┌─────────────────────────────────────┐
│ React validates before sending:      │
│ ✓ Customer selected?                │
│ ✓ Quantity > 0?                     │
│ ✓ Price > 0?                        │
│ ✓ Line items exist?                 │
│ If all pass → continue              │
│ If fail → show error to user        │
└─────────────────────────────────────┘
                  ↓
STEP 3: Send to Backend
┌─────────────────────────────────────┐
│ POST /api/v1/sales                  │
│ Headers:                            │
│   Authorization: "Bearer token"     │
│   Content-Type: "application/json"  │
│ Body (JSON):                        │
│ {                                   │
│   "customer_id": "CUST-001",        │
│   "line_items": [                   │
│     {                               │
│       "item_id": "bottle-500ml-a",  │
│       "quantity": 100,              │
│       "unit_price": 4.00            │
│     },                              │
│     {                               │
│       "item_id": "bottle-1500ml-a", │
│       "quantity": 50,               │
│       "unit_price": 6.00            │
│     }                               │
│   ],                                │
│   "due_date": "2025-12-30",         │
│   "notes": "Fast delivery needed"   │
│ }                                   │
└─────────────────────────────────────┘
                  ↓
STEP 4: Backend Authentication
┌─────────────────────────────────────┐
│ FastAPI middleware:                 │
│ 1. Extract token from header        │
│ 2. Verify token (check signature)   │
│ 3. Check if expired                 │
│ 4. Extract user_id from token       │
│ If anything fails → Return 401      │
└─────────────────────────────────────┘
                  ↓
STEP 5: Request Validation
┌─────────────────────────────────────┐
│ Pydantic schema validates:          │
│ ✓ customer_id is string?            │
│ ✓ line_items is list?               │
│ ✓ Each item has required fields?    │
│ ✓ quantity is integer > 0?          │
│ ✓ unit_price is decimal > 0?        │
│ If any fail → Return 422 (Unprocessable)
└─────────────────────────────────────┘
                  ↓
STEP 6: Business Logic Validation
┌─────────────────────────────────────┐
│ Check business rules:               │
│ 1. Does customer exist?             │
│    SELECT * FROM customers          │
│    WHERE id = 'CUST-001'            │
│    If NOT found → 404 error         │
│                                     │
│ 2. Does item 1 exist?               │
│    SELECT * FROM items              │
│    WHERE id = 'bottle-500ml-a'      │
│    If NOT found → 404 error         │
│                                     │
│ 3. Is stock sufficient?             │
│    SELECT quantity FROM stocks      │
│    WHERE item_id = 'bottle-500ml-a' │
│    If quantity < 100 → Error        │
│                                     │
│ 4. Repeat for item 2...             │
│                                     │
│ 5. Is user authorized?              │
│    Is user role 'admin' or          │
│    'sales_manager'?                 │
│    If user role = 'view_only'       │
│    → 403 Forbidden                  │
└─────────────────────────────────────┘
                  ↓
STEP 7: Generate Bill Number
┌─────────────────────────────────────┐
│ Generate unique bill_number:        │
│ Format: SO-{YY}{MM}{DD}-{SEQ}       │
│ Query last bill today:              │
│   SELECT bill_number FROM sales     │
│   WHERE date >= TODAY()             │
│   ORDER BY created_at DESC LIMIT 1  │
│ Last bill was: SO-251223-0025       │
│ New bill: SO-251223-0026            │
└─────────────────────────────────────┘
                  ↓
STEP 8: Create Sale Record
┌─────────────────────────────────────┐
│ INSERT INTO sales:                  │
│ bill_number: 'SO-251223-0026'       │
│ customer_id: 'CUST-001'             │
│ total_price: 700.00 (100*4 + 50*6)  │
│ status: 'confirmed'                 │
│ payment_status: 'pending'           │
│ created_by: 'USER-RAJ'              │
│ date: 2025-12-23 14:30:00           │
│ notes: 'Fast delivery needed'       │
│                                     │
│ Returns: Sale object with new ID    │
└─────────────────────────────────────┘
                  ↓
STEP 9: Create Line Items
┌─────────────────────────────────────┐
│ For each line item:                 │
│ INSERT INTO sale_line_items:        │
│                                     │
│ Item 1:                             │
│   id: 'SALE-LI-001'                 │
│   bill_number: 'SO-251223-0026'     │
│   item_id: 'bottle-500ml-a'         │
│   quantity: 100                     │
│   unit_price: 4.00                  │
│   total_price: 400.00               │
│                                     │
│ Item 2:                             │
│   id: 'SALE-LI-002'                 │
│   bill_number: 'SO-251223-0026'     │
│   item_id: 'bottle-1500ml-a'        │
│   quantity: 50                      │
│   unit_price: 6.00                  │
│   total_price: 300.00               │
└─────────────────────────────────────┘
                  ↓
STEP 10: Update Stock
┌─────────────────────────────────────┐
│ For each line item:                 │
│ UPDATE stocks SET quantity = ?      │
│                                     │
│ Item 1:                             │
│   SELECT quantity FROM stocks       │
│   WHERE item_id = 'bottle-500ml-a'  │
│   Current: 500                      │
│   New: 500 - 100 = 400              │
│   UPDATE stocks SET quantity = 400  │
│                                     │
│ Item 2:                             │
│   SELECT quantity FROM stocks       │
│   WHERE item_id = 'bottle-1500ml-a' │
│   Current: 250                      │
│   New: 250 - 50 = 200               │
│   UPDATE stocks SET quantity = 200  │
└─────────────────────────────────────┘
                  ↓
STEP 11: Calculate Profit (Optional)
┌─────────────────────────────────────┐
│ For reporting, track cost:          │
│ SELECT cost_basis FROM stock_moves  │
│ WHERE item_id = 'bottle-500ml-a'    │
│ Average cost per unit: $3.50        │
│                                     │
│ Item 1 profit:                      │
│   Revenue: 100 * $4 = $400          │
│   Cost: 100 * $3.50 = $350          │
│   Profit: $50                       │
│                                     │
│ Item 2 profit:                      │
│   Revenue: 50 * $6 = $300           │
│   Cost: 50 * $4.20 = $210           │
│   Profit: $90                       │
│                                     │
│ Total profit: $140                  │
└─────────────────────────────────────┘
                  ↓
STEP 12: Return Success Response
┌─────────────────────────────────────┐
│ HTTP 201 Created                    │
│ {                                   │
│   "bill_number": "SO-251223-0026",  │
│   "customer_id": "CUST-001",        │
│   "total_price": 700.00,            │
│   "status": "confirmed",            │
│   "line_items": [                   │
│     {                               │
│       "item_id": "bottle-500ml-a",  │
│       "quantity": 100,              │
│       "profit": 50.00               │
│     },                              │
│     {                               │
│       "item_id": "bottle-1500ml-a", │
│       "quantity": 50,               │
│       "profit": 90.00               │
│     }                               │
│   ],                                │
│   "total_profit": 140.00,           │
│   "created_at": "2025-12-23T..."    │
│ }                                   │
└─────────────────────────────────────┘
                  ↓
STEP 13: Frontend Receives Response
┌─────────────────────────────────────┐
│ React receives success response      │
│ 1. Parse JSON                       │
│ 2. Check if status is 201           │
│ 3. Show success message to user     │
│   "Sale created! Bill: SO-251223..."│
│ 4. Refresh sales list               │
│   GET /api/v1/sales                 │
│ 5. Update dashboard                 │
│   Show new total revenue            │
│ 6. Navigate to sale details page    │
│   (Optional) Show bill preview      │
└─────────────────────────────────────┘
```

### Error Scenarios

```
What if stock is insufficient?

User tries to sell 500 bottles but only 200 in stock.

Flow:
1. User submits sale for 500 units
2. Backend checks stock (STEP 6)
3. Finds: stock = 200, requested = 500
4. Check fails! Return 400 Bad Request
5. Response: {
     "error": "Insufficient stock",
     "item_id": "bottle-500ml-a",
     "available": 200,
     "requested": 500,
     "shortage": 300
   }
6. Frontend shows error message
7. User adjusts quantity to 200
8. Resubmits → Success

What if customer doesn't exist?

User enters non-existent customer ID.

Flow:
1. User submits sale with customer_id = "CUST-999"
2. Backend checks if customer exists (STEP 6)
3. Query: SELECT * FROM customers WHERE id = 'CUST-999'
4. Result: NOT FOUND
5. Return 404 Not Found
6. Response: {
     "error": "Customer not found",
     "customer_id": "CUST-999"
   }
7. Frontend shows error
8. User selects valid customer
9. Resubmits → Success
```

---

## QUESTION: What are the security concerns?

### Threats and Mitigations

```
THREAT 1: Password Guessing
Problem: Attacker tries random passwords until one works
Mitigation:
  - Bcrypt makes each attempt take 0.2s (vs instant)
  - Even if 1000 guesses/second, 1 million passwords = 1000s = 17 mins
  - Most locks after 5 wrong attempts
  - Implement rate limiting (max 5 login attempts per minute)
  - Status: ✅ WELL PROTECTED

THREAT 2: Database Breach
Problem: Hacker steals database
What's at risk:
  ❌ Customer names, addresses (high value for marketing fraud)
  ❌ Business data (sales, suppliers, strategies)
  ✅ Passwords (safely hashed, can't be reversed)
  ✅ Payment methods (not stored, only transaction records)
Mitigation:
  - Database on Neon (enterprise-grade security)
  - Regular backups (can restore if encrypted)
  - Encryption at rest (database is encrypted)
  - Access control (only backend can access)
  - Audit logs (all access tracked)
  - Status: ⚠️ MODERATE RISK

THREAT 3: API Token Theft
Problem: Someone steals a user's JWT token
Impact: Can impersonate user, access their data/make transactions
Mitigation:
  - Token expires after 24 hours (limited damage window)
  - HTTPS only (token encrypted in transit)
  - localStorage is same-origin (other websites can't access)
  - Implement logout → invalidate token
  - Monitor for suspicious activity
  - Force password change if breach suspected
  - Status: ✅ WELL PROTECTED

THREAT 4: SQL Injection
Problem: Attacker sends malicious SQL in input
Example: username = "admin'; DROP TABLE users;--"
Impact: Delete tables, modify data, steal data
Mitigation:
  - Using SQLAlchemy ORM (parameterized queries)
  - Input validation (Pydantic schemas)
  - Type checking (enforces data types)
  - Status: ✅ WELL PROTECTED

THREAT 5: CSRF (Cross-Site Request Forgery)
Problem: User visits evil.com while logged in
evil.com makes request to api.com pretending to be user
Impact: Unauthorized transactions in user's account
Mitigation:
  - CORS set to specific domain (prevent cross-origin requests)
  - JWT tokens (only in Authorization header, not cookies)
  - Status: ✅ WELL PROTECTED

THREAT 6: Man-in-the-Middle Attack
Problem: Attacker intercepts HTTP traffic
Impact: Steal tokens, passwords, sensitive data
Mitigation:
  - HTTPS enforced (all traffic encrypted)
  - TLS 1.3 (latest encryption standard)
  - Certificate pinning (prevent fake certificates)
  - Status: ✅ WELL PROTECTED

THREAT 7: Unauthorized Access
Problem: User tries to access data they shouldn't
Example: Regular user tries to delete admin account
Impact: Data breach, fraud
Mitigation:
  - Role-based access control (RBAC)
  - Check user role on every request
  - Different permissions for admin vs user vs viewer
  - Audit logs (track who did what)
  - Status: ⚠️ NEEDS IMPROVEMENT (no explicit RBAC mentioned in code)

THREAT 8: DDoS (Distributed Denial of Service)
Problem: Attacker floods server with requests
Impact: Server overloaded, legitimate users can't access
Mitigation:
  - Rate limiting (max requests per minute per IP)
  - Load balancer (distribute traffic)
  - CDN (absorbs traffic)
  - Auto-scaling (add more servers when needed)
  - Status: ✅ WELL PROTECTED (Railway handles this)
```

---

## QUESTION: How would you scale this to 1 million users?

### Scaling Strategy

```
Current Setup (Small Business):
- 1 backend server (FastAPI on Railway)
- 1 database (PostgreSQL on Neon)
- Frontend on Vercel
- 20 concurrent users
- Works perfectly fine

Scaling to 1,000 Users:
Same setup, just upgrade database size
- More RAM for PostgreSQL
- Larger storage
- Cost: $50/month → $100/month

Scaling to 10,000 Users:
Multi-server setup needed:
┌──────────────────────────────────────┐
│ Load Balancer                        │
│ (Routes requests)                    │
└──────────────────────────────────────┘
    ↓         ↓         ↓
┌────────┐ ┌────────┐ ┌────────┐
│Backend1│ │Backend2│ │Backend3│
│FastAPI │ │FastAPI │ │FastAPI │
└────────┘ └────────┘ └────────┘
    ↓         ↓         ↓
┌──────────────────────────────────────┐
│ Database Pool                        │
└──────────────────────────────────────┘
    ↓
┌──────────────────────────────────────┐
│ PostgreSQL Primary                   │
│ (Handles writes)                     │
└──────────────────────────────────────┘
    ↓         ↓
┌────────────────────────────────────┐
│ Replica 1 (Read-only for reports)  │
│ Replica 2 (Backup/failover)        │
└────────────────────────────────────┘

Changes needed:
1. Add 2 more backend servers
2. Setup load balancer (AWS ALB, Nginx)
3. Database read replicas (for reports)
4. Caching layer (Redis)
5. CDN for frontend
Cost: $100/month → $500/month

Scaling to 100,000 Users:
Add caching & optimization:
┌──────────────────────────────────────┐
│ Cdn (Cloudflare)                    │
│ (Cache frontend, DDoS protection)    │
└──────────────────────────────────────┘
    ↓
┌──────────────────────────────────────┐
│ Load Balancer (AWS ALB)              │
└──────────────────────────────────────┘
    ↓
┌──────────────────────────────────────┐
│ Auto-scaling Group                   │
│ (5-10 backend servers, scales up     │
│  during peak hours)                  │
└──────────────────────────────────────┘
    ↓
┌──────────────────────────────────────┐
│ Cache Layer (Redis)                  │
│ (Cache stock, customer data,         │
│  recently calculated reports)        │
└──────────────────────────────────────┘
    ↓
┌──────────────────────────────────────┐
│ Message Queue (RabbitMQ)             │
│ (For async tasks like report gen,    │
│  email notifications)                │
└──────────────────────────────────────┘
    ↓
┌──────────────────────────────────────┐
│ Reporting Database                   │
│ (Separate read replica for analytics)│
└──────────────────────────────────────┘
    ↓
┌──────────────────────────────────────┐
│ Main Database                        │
│ (Partitioned by date/region)         │
└──────────────────────────────────────┘

Code changes:
1. Add Redis integration for caching
2. Add message queue for async tasks
3. Implement connection pooling
4. Add database sharding (partition by region)
5. Separate write vs read databases
6. Add monitoring (Prometheus, Grafana)
7. Add distributed tracing (Jaeger)
Cost: $500/month → $2000/month

Scaling to 1,000,000 Users:
Enterprise architecture:
1. Kubernetes for container orchestration
2. Elasticsearch for search
3. Data warehouse (Snowflake) for analytics
4. Event streaming (Kafka) for real-time data
5. Microservices (separate services for inventory, sales, reports)
6. Multi-region deployment
7. Advanced security (OAuth2, SSO)
Cost: $2000/month → $10,000+/month
```

### Scaling Challenges

```
1. Database Bottleneck
Problem: Even with optimization, can't scale queries beyond a point
Solution:
  - Sharding (split by region/customer)
  - Data warehouse (Snowflake, BigQuery for analytics)
  - Event sourcing (store events, not state)

2. Consistency vs Performance
Problem: More servers = harder to keep data consistent
Solution:
  - Eventually consistent architecture
  - Saga pattern for distributed transactions
  - Accept slight staleness in cached data

3. Operational Complexity
Problem: More servers = harder to manage
Solution:
  - Infrastructure as Code (Terraform)
  - Kubernetes for orchestration
  - CI/CD automation
  - Monitoring dashboards

4. Cost
Problem: Scaling costs money
Solution:
  - Optimize queries first (cheaper than more hardware)
  - Use serverless (pay per request)
  - Right-size infrastructure
```

---

**End of Deep Dive**

These answers should handle 90% of system design interview questions!
