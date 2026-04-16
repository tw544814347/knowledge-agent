"""认证依赖注入"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from ..models.schemas import User
from .user_manager import UserManager

security = HTTPBearer(auto_error=False)

# 全局用户管理器实例
_user_manager: Optional[UserManager] = None

def set_user_manager(user_manager: UserManager) -> None:
    """设置全局用户管理器实例"""
    global _user_manager
    _user_manager = user_manager

def get_user_manager() -> UserManager:
    """获取用户管理器实例"""
    if _user_manager is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="用户管理器未初始化"
        )
    return _user_manager

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """获取当前用户（可选，用于兼容未登录用户）"""
    if not credentials:
        return None
    
    user_manager = get_user_manager()
    user = user_manager.get_current_user(credentials.credentials)
    return user

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """获取当前用户（必须登录）"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_manager = get_user_manager()
    user = user_manager.get_current_user(credentials.credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user