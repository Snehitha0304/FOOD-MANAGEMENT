from fastapi import Depends
from app.core.security import require_role
from app.core.constants import UserRole

get_current_admin = require_role(UserRole.ADMIN)

__all__ = ["get_current_admin"]
