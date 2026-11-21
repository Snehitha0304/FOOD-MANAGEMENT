import logging
from typing import Optional, Union
from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.constants import UserRole
from app.schemas.auth import UserRegister, UserLogin, UserCreateAdmin, Token, UserResponse
from app.services.auth_service import auth_service
from app.dependencies.admin import get_current_admin
from app.models.users import User

logger = logging.getLogger("audit")
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register as customer (User Story 1)"
)
def register_customer(
    data: UserRegister,
    db: Session = Depends(get_db)
):
    return auth_service.register_customer(db, data)


@router.post(
    "/login",
    response_model=Token,
    summary="Log in with email/password and receive JWT (User Story 4)"
)
def login(
    request: Request,
    data: Optional[UserLogin] = None,
    form_data: Optional[OAuth2PasswordRequestForm] = Depends(lambda: None),
    db: Session = Depends(get_db)
):
    # Support both JSON request body and Swagger OAuth2PasswordRequestForm
    if data:
        email = data.email
        password = data.password
    elif form_data:
        email = form_data.username
        password = form_data.password
    else:
        from app.core.exceptions import BadRequestException
        raise BadRequestException("Missing login credentials", code="CREDENTIALS_MISSING")

    login_dto = UserLogin(email=email, password=password)
    return auth_service.login(db, login_dto)


@router.post(
    "/admin/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Admin onboarding for Restaurant Owner or Delivery Agent (User Stories 2 & 3)"
)
def admin_create_user(
    data: UserCreateAdmin,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return auth_service.admin_create_user(db, data)
