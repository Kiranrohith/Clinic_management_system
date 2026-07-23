from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from app.api.dependencies import get_current_active_user


def require_roles(*allowed_roles: str) -> Callable:
    def _checker(current_user=Depends(get_current_active_user)):
        if current_user.role.role_name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource.",
            )
        return current_user

    return _checker
