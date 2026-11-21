from fastapi import Depends
from app.core.security import require_role
from app.core.constants import UserRole

get_current_owner = require_role(UserRole.RESTAURANT_OWNER)

__all__ = ["get_current_owner"]
