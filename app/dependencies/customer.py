from fastapi import Depends
from app.core.security import require_role
from app.core.constants import UserRole

get_current_customer = require_role(UserRole.CUSTOMER)

__all__ = ["get_current_customer"]
