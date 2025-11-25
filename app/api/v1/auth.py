from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.db.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, get_current_user
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, Token, UserResponse

router = APIRouter()

@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Create new user
    db_user = User(
        id=user_data.id,
        username=user_data.username,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": db_user.id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(db_user)
    }

@router.post("/login", response_model=Token)
async def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"📝 Login attempt for username: {user_login.username}")
        
        # Make username lookup case-insensitive
        user = db.query(User).filter(
            User.username.ilike(user_login.username)
        ).first()
        
        if not user:
            logger.warning(f"❌ Login attempt for non-existent user: {user_login.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"   ✅ User found: {user.username}")
        
        # Verify password (plain text comparison)
        logger.info(f"🔐 Verifying password...")
        if not verify_password(user_login.password, user.password_hash):
            logger.warning(f"❌ Failed login for user: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"✅ Successful login for user: {user.username}")
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user.id},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse.from_orm(user)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected login error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/test-db")
async def test_db(db: Session = Depends(get_db)):
    """Test database connection"""
    try:
        # Try a simple query
        users = db.query(User).limit(1).all()
        return {
            "status": "success",
            "message": "Database connection OK",
            "user_count": len(users)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@router.get("/migrate-database")
async def migrate_database(db: Session = Depends(get_db)):
    """Run database migrations - Add missing columns to extra_expenditures table"""
    try:
        from sqlalchemy import text, inspect
        from sqlalchemy.orm import Session as SQLSession
        
        print("🔄 Starting database migration...")
        
        # Check if extra_expenditures table exists
        inspector = inspect(db.get_bind())
        tables = inspector.get_table_names()
        
        if 'extra_expenditures' not in tables:
            print("📋 Creating extra_expenditures table...")
            # Table doesn't exist, create it
            from app.models.transaction import ExtraExpenditure
            from app.db.database import Base
            Base.metadata.create_all(db.get_bind())
            return {
                "status": "success",
                "message": "extra_expenditures table created",
                "migrations": ["Created extra_expenditures table"]
            }
        
        # Get existing columns
        existing_columns = [c['name'] for c in inspector.get_columns('extra_expenditures')]
        print(f"Current columns: {existing_columns}")
        
        # Define columns that need to be added
        columns_to_add = [
            ("expense_type", "VARCHAR NOT NULL DEFAULT 'General'"),
            ("description", "TEXT"),
            ("amount", "NUMERIC(12, 2) NOT NULL DEFAULT 0"),
            ("date", "DATE NOT NULL DEFAULT CURRENT_DATE"),
            ("notes", "TEXT"),
            ("created_by", "VARCHAR"),
            ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
        ]
        
        migrations_performed = []
        
        # Add missing columns
        for col_name, col_definition in columns_to_add:
            if col_name not in existing_columns:
                print(f"Adding column: {col_name}...")
                db.execute(text(
                    f"ALTER TABLE extra_expenditures ADD COLUMN {col_name} {col_definition}"
                ))
                migrations_performed.append(f"Added column {col_name}")
                print(f"✅ Column {col_name} added")
            else:
                print(f"Column {col_name} already exists")
        
        db.commit()
        
        if migrations_performed:
            print(f"✅ Migration completed! Performed {len(migrations_performed)} migrations")
            return {
                "status": "success",
                "message": "Database migration completed",
                "migrations": migrations_performed
            }
        else:
            print("ℹ️ No migrations needed")
            return {
                "status": "success",
                "message": "Database already up to date",
                "migrations": []
            }
        
    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"❌ Migration failed: {error_msg}")
        return {
            "status": "error",
            "message": f"Migration failed: {str(e)}",
            "error_detail": error_msg
        }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse.from_orm(current_user)
