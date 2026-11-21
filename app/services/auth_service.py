import logging
from sqlalchemy.orm import Session
from app.models.users import User
from app.schemas.auth import UserRegister, UserLogin, UserCreateAdmin, Token, UserResponse
from app.repositories.user_repository import user_repository
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.constants import UserRole
from app.core.exceptions import ConflictException, UnauthorizedException, BadRequestException

logger = logging.getLogger("audit")


class AuthService:
    def register_customer(self, db: Session, data: UserRegister) -> UserResponse:
        existing = user_repository.get_by_email(db, data.email)
        if existing:
            raise ConflictException(f"User with email '{data.email}' already exists", code="EMAIL_ALREADY_EXISTS")
        
        user = User(
            email=data.email,
            password_hash=get_password_hash(data.password),
            full_name=data.full_name,
            phone=data.phone,
            role=UserRole.CUSTOMER,
            is_active=True
        )
        created_user = user_repository.create(db, user)
        logger.info(f"AUDIT: Customer registered successfully with ID {created_user.id} and email {created_user.email}")
        return UserResponse.model_validate(created_user)

    def login(self, db: Session, data: UserLogin) -> Token:
        user = user_repository.get_by_email(db, data.email)
        if not user or not verify_password(data.password, user.password_hash):
            logger.warning(f"AUDIT: Failed login attempt for email {data.email}")
            raise UnauthorizedException("Incorrect email or password", code="INVALID_CREDENTIALS")
        
        if not user.is_active:
            logger.warning(f"AUDIT: Login attempt on inactive account {user.id}")
            raise UnauthorizedException("User account is inactive", code="INACTIVE_USER")

        token_data = {
            "sub": str(user.id),
            "role": user.role.value if hasattr(user.role, "value") else str(user.role),
            "email": user.email
        }
        access_token = create_access_token(data=token_data)
        logger.info(f"AUDIT: Successful login for user ID {user.id} with role {user.role.value}")
        return Token(
            access_token=access_token,
            token_type="bearer",
            role=user.role,
            user_id=user.id
        )

    def admin_create_user(self, db: Session, data: UserCreateAdmin) -> UserResponse:
        existing = user_repository.get_by_email(db, data.email)
        if existing:
            raise ConflictException(f"User with email '{data.email}' already exists", code="EMAIL_ALREADY_EXISTS")

        user = User(
            email=data.email,
            password_hash=get_password_hash(data.password),
            full_name=data.full_name,
            phone=data.phone,
            role=data.role,
            is_active=True
        )
        created_user = user_repository.create(db, user)
        logger.info(f"AUDIT: Admin created user ID {created_user.id} with role {created_user.role.value}")
        return UserResponse.model_validate(created_user)


auth_service = AuthService()
