import jwt

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm

from app.models.users import User as UserModel
from app.schemas import (
    UserCreate,
    RefreshTokenRequest,
)
from app.db_depends import get_async_db
from app.config import SECRET_KEY, ALGORITHM, SUPER_USER_SECRET_KEY
from datetime import datetime
from app.auth.auth import (
    create_refresh_token,
    get_current_admin,
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/create-admin", status_code=status.HTTP_201_CREATED
)
async def create_admin(
    new_admin: UserCreate, secret_key: str, db: AsyncSession = Depends(get_async_db)
):
    """This endpoint implemented to create admin role users. 
    
    Configs for secret_key should be written in .env"""
    
    if secret_key != SUPER_USER_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect secret key"
        )
    
    user_email_stmt = await db.scalars(
        select(UserModel).where(UserModel.email == new_admin.email)
    )
    
    user_email = user_email_stmt.first()
    
    if user_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
            )
        
    
    db_user = UserModel(
        email=new_admin.email,
        hashed_password=hash_password(new_admin.password),
        role="admin",
    )
    
    db.add(db_user)
    await db.commit()
    return {"message": f"Admin {new_admin.email} was successfully created !"}





@router.post(
    "/create-specialist", status_code=status.HTTP_201_CREATED
)
async def create_specialist(
    new_specialist: UserCreate, user_admin: UserModel = Depends(get_current_admin), db: AsyncSession = Depends(get_async_db)
):
    """This endpoint implemented to create specialist role users.  Only admins can create specialists."""
    
    
    user_email_stmt = await db.scalars(
        select(UserModel).where(UserModel.email == new_specialist.email)
    )
    
    user_email = user_email_stmt.first()
    
    if user_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
            )
        
    
    db_user = UserModel(
        email=new_specialist.email,
        hashed_password=hash_password(new_specialist.password),
        role="specialist",
    )
    
    db.add(db_user)
    await db.commit()
    return {"message": f"Specialist {new_specialist.email} was successfully created !"}





@router.post(
    "/create-ai-developer", status_code=status.HTTP_201_CREATED
)
async def create_ai_developer(
    new_ai_developer: UserCreate, user_admin: UserModel = Depends(get_current_admin), db: AsyncSession = Depends(get_async_db)
):
    """This endpoint implemented to create "ai-developer" role users.  Only admins can create "ai-developers"."""
    
    
    user_email_stmt = await db.scalars(
        select(UserModel).where(UserModel.email == new_ai_developer.email)
    )
    
    user_email = user_email_stmt.first()
    
    if user_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
            )
        
    
    db_user = UserModel(
        email=new_ai_developer.email,
        hashed_password=hash_password(new_ai_developer.password),
        role="ai_developer",
    )
    
    db.add(db_user)
    await db.commit()
    return {"message": f"AI-developer {new_ai_developer.email} was successfully created !"}





@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db),
):
    """Аутиентифицирует пользователя и возвращает  JWT с  e-mail, role и id"""
    result = await db.scalars(
        select(UserModel).where(
            UserModel.email == form_data.username, UserModel.is_active == True
        )
    )
    user = result.first()
    if (not user) or (not verify_password(form_data.password, user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect e-mail or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "id": user.id}
    )

    refresh_token = create_refresh_token(
        data={"sub": user.email, "role": user.role, "id": user.id}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
    
    
    

@router.post("/refresh-token")
async def refresh_token(
    body: RefreshTokenRequest, db: AsyncSession = Depends(get_async_db)
):
    """Обновляет refresh-токен, принимая старый refresh-токен в теле запроса."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    old_refresh_token = body.refresh_token
    try:
        payload = jwt.decode(old_refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        token_type: str | None = payload.get("token_type")

        if email is None or token_type != "refresh":
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user_stmt = await db.scalars(
        select(UserModel).where(UserModel.email == email, UserModel.is_active == True)
    )
    user = user_stmt.first()

    if user is None:
        raise credentials_exception

    new_refresh_token = create_refresh_token(
        data={"sub": email, "role": user.role, "id": user.id}
    )
    return {
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.post("/new-token")
async def create_new_access_token(
    body: RefreshTokenRequest, db: AsyncSession = Depends(get_async_db)
):
    credentials_exceptions = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    refresh_token = body.refresh_token
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        token_type = payload.get("token_type")

        if (email is None) or (token_type != "refresh"):
            raise credentials_exceptions

        user = (
            await db.scalars(
                select(UserModel).where(
                    UserModel.email == email, UserModel.is_active == True
                )
            )
        ).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or deactivated",
            )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise credentials_exceptions

    access_token = create_access_token(
        data={"sub": email, "role": payload.get("role"), "id": payload.get("id")}
    )
    return {"access_token": access_token, "token_type": "bearer"}
