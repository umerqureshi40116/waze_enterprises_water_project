from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.database import get_db
from app.models.user import User

# Lazy load pwd_context to avoid initialization errors
_pwd_context = None

def get_pwd_context():
    global _pwd_context
    if _pwd_context is None:
        _pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return _pwd_context

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def verify_password(plain_password: str, stored_password: str) -> bool:
    """Compare plain text passwords - no hashing"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"🔐 Comparing passwords (plain text):")
    logger.info(f"   Input length: {len(plain_password)}")
    logger.info(f"   Stored length: {len(stored_password)}")
    
    # Simple string comparison
    result = plain_password == stored_password
    logger.info(f"   Match result: {result}")
    return result

def get_password_hash(password: str) -> str:
    """Store password as plain text - no hashing"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"📝 Storing password (plain text):")
    logger.info(f"   Password length: {len(password)}")
    
    # Just return the password as-is (plain text storage)
    return password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    import logging
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            logging.error(f"JWT payload missing 'sub': {payload}")
            raise credentials_exception
    except JWTError as e:
        logging.error(f"JWTError during token decode: {e}")
        raise credentials_exception
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        logging.error(f"User not found for id: {user_id}")
        raise credentials_exception
    return user

async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
