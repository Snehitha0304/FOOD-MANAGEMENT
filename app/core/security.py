import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.core.database import get_db

logger = logging.getLogger("audit")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    now_utc = datetime.now(timezone.utc)
    if expires_delta:
        expire = now_utc + expires_delta
    else:
        expire = now_utc + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": now_utc})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.warning(f"JWT verification failed: {str(e)}")
        raise UnauthorizedException("Invalid token or token expired", code="INVALID_TOKEN")


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    from app.models.users import User
    if not token:
        raise UnauthorizedException("Authentication credentials were not provided", code="AUTHENTICATION_REQUIRED")
    
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    role = payload.get("role")
    if user_id is None:
        raise UnauthorizedException("Invalid token payload", code="INVALID_TOKEN")
    
    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        raise UnauthorizedException("Invalid user id in token", code="INVALID_TOKEN")

    user = db.query(User).filter(User.id == user_id_int).first()
    if not user:
        raise UnauthorizedException("User not found", code="USER_NOT_FOUND")
    if not user.is_active:
        raise ForbiddenException("User account is inactive", code="INACTIVE_USER")
    
    return user


def require_role(*allowed_roles: str):
    def role_checker(current_user = Depends(get_current_user)):
        user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
        allowed_values = [r.value if hasattr(r, "value") else str(r) for r in allowed_roles]
        if user_role not in allowed_values:
            logger.warning(
                f"Access denied for user {current_user.id} ({user_role}). Allowed roles: {allowed_values}"
            )
            raise ForbiddenException(
                detail=f"Operation requires one of the following roles: {', '.join(allowed_values)}",
                code="ROLE_NOT_AUTHORIZED"
            )
        return current_user
    return role_checker
