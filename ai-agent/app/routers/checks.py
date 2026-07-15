from fastapi import APIRouter, Depends, File, Form, UploadFile, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db_depends import get_async_db
from app.services.package_service import PackageService
from app.auth.auth import get_current_user
from app.models.users import User as UserModel
from app.schemas import CheckListItem, CheckResponse

router = APIRouter(prefix="/api/checks", tags=["checks"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_check(
    package_id: str | None = Form(None),
    program: str = Form(...),
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_user)
):
    if (current_user.role == "specialist") or (current_user.role == "admin"):
        
        service = PackageService(db)
        try:
            result = await service.create_package_version(
                files=files, program=program, package_id=package_id
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

        return result
    else:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Only admins and specialist can perform this action")


@router.get("/", response_model=List[CheckListItem])
async def list_checks(
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_user),
):
    service = PackageService(db)
    checks = await service.list_checks()
    return [
        {
            "package_id": group["package_id"],
            "package_version_ids": group["package_version_ids"],
            "date": group["latest_created_at"],
            "program": group["latest_program"],
            "status": group["latest_status"],
            "document_count": group["document_count"],
        }
        for group in checks
    ]


@router.get("/{package_version_id}", response_model=CheckResponse)
async def get_check(
    package_version_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_user),
):
    service = PackageService(db)
    return await service.get_check_by_id(package_version_id)




