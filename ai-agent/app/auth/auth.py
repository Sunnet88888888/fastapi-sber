from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
import jwt

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.users import User as UserModel
from app.config import SECRET_KEY, ALGORITHM
from app.db_depends import get_async_db
from app.auth.hashing import hash_password, verify_password

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


oauth2scheme = OAuth2PasswordBearer(tokenUrl="users/token")


def create_access_token(data: dict):
    """Создаёт JWT с payload (sub, role, id, exp)."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "token_type": "access"})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    """
    Создаёт refresh-токен с длительным сроком действия и token_type="refresh".
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "token_type": "refresh"})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    token: str = Depends(oauth2scheme), db: AsyncSession = Depends(get_async_db)
):
    """Проверяет JWT и возвращает пользователя из базы."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    result = await db.scalars(
        select(UserModel).where(UserModel.email == email, UserModel.is_active == True)
    )
    user = result.first()
    if user is None:
        raise credentials_exception

    return user


async def get_current_specialist(current_user: UserModel = Depends(get_current_user)):
    if current_user.role != "specialist":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only specialists can perform this action",
        )
    return current_user


async def get_current_admin(current_user: UserModel = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can perform this action",
        )
    return current_user


async def get_current_super_user(current_user: UserModel = Depends(get_current_user)):
    if current_user.role != "super_user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super_users can perform this action",
        )
    return current_user


async def get_current_ai_developer(current_user: UserModel = Depends(get_current_user)):
    if current_user.role != "ai_developer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ai_developers can perform this action",
        )
    return current_user
