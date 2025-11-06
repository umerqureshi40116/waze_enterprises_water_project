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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    import logging
    logger = logging.getLogger(__name__)
    
    # Bcrypt has 72-byte limit - truncate to be safe
    plain_password = plain_password[:72]
    logger.debug(f"Verifying password: input length={len(plain_password)}, hash length={len(hashed_password)}")
    logger.debug(f"Hash value: {hashed_password[:50]}...")
    
    try:
        result = pwd_context.verify(plain_password, hashed_password)
        logger.debug(f"Password verification result: {result}")
        return result
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        raise

def get_password_hash(password: str) -> str:
    import logging
    logger = logging.getLogger(__name__)
    
    # Bcrypt has 72-byte limit - truncate to be safe
    password = password[:72]
    logger.debug(f"Hashing password: input length={len(password)}")
    try:
        hash_result = pwd_context.hash(password)
        logger.debug(f"Hash result length: {len(hash_result)}")
        return hash_result
    except Exception as e:
        logger.error(f"Password hashing error: {e}")
        raise

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
