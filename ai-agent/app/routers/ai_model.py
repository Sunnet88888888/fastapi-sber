from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_depends import get_async_db
from app.services.package_service import PackageService
from app.auth.auth import get_current_ai_developer
from app.schemas import AIUncheckedPackageResponse, AIPackageDocumentsResponse, AICheckResult

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.get("/next-unchecked-package", response_model=AIUncheckedPackageResponse)
async def get_next_unchecked_package(
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_ai_developer),
):
    service = PackageService(db)
    package_id = await service.get_next_unchecked_package_id()
    return {"package_id": package_id}


@router.get("/packages/{package_id}/documents", response_model=AIPackageDocumentsResponse)
async def get_package_documents(
    package_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_ai_developer),
):
    service = PackageService(db)
    return await service.get_package_documents(package_id)


@router.post("/checked_package/{package_id}")
async def post_checked_package(
    package_id: str,
    body: AICheckResult,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_ai_developer),
):
    service = PackageService(db)
    result = await service.accept_checked_package(package_id, body.model_dump())
    return result


