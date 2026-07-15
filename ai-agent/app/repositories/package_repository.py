from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.packages import PackageModel
from app.models.package_versions import PackageVersionModel
from app.models.documents import DocumentModel
from app.models.issues import IssueModel
from sqlalchemy.orm import selectinload


class PackageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, package_id: str) -> PackageModel | None:
        result = await self.session.scalar(
            select(PackageModel).where(PackageModel.id == package_id)
        )
        return result

    async def create(self, created_by: str | None = None) -> PackageModel:
        package = PackageModel(created_by=created_by, current_version=1)
        self.session.add(package)
        await self.session.flush()
        return package


class PackageVersionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        package_id: str,
        version: int,
        program: str,
        status: str,
        status_label: str,
        reason: str | None,
    ) -> PackageVersionModel:
        version_entity = PackageVersionModel(
            package_id=package_id,
            version=version,
            program=program,
            status=status,
            status_label=status_label,
            reason=reason,
            extracted=None,
            checked_at=None,
        )
        self.session.add(version_entity)
        await self.session.flush()
        return version_entity

    async def list_checks(self) -> list[dict]:
        stmt = (
            select(
                PackageVersionModel.package_id,
                PackageVersionModel.id.label("package_version_id"),
                PackageVersionModel.created_at,
                PackageVersionModel.program,
                PackageVersionModel.status,
                func.count(DocumentModel.id).label("document_count"),
            )
            .outerjoin(DocumentModel, PackageVersionModel.id == DocumentModel.package_version_id)
            .group_by(
                PackageVersionModel.package_id,
                PackageVersionModel.id,
                PackageVersionModel.created_at,
                PackageVersionModel.program,
                PackageVersionModel.status,
            )
            .order_by(PackageVersionModel.package_id.asc(), PackageVersionModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return [dict(row) for row in result.mappings().all()]

    async def get_check_by_id(self, package_version_id: str) -> PackageVersionModel | None:
        result = await self.session.execute(
            select(PackageVersionModel)
            .options(
                selectinload(PackageVersionModel.documents),
                selectinload(PackageVersionModel.issues),
            )
            .where(PackageVersionModel.id == package_version_id)
        )
        return result.scalar_one_or_none()

    async def get_earliest_unchecked_package_id(self) -> str | None:
        result = await self.session.execute(
            select(PackageVersionModel.package_id)
            .where(PackageVersionModel.status == "check_in_progress")
            .order_by(PackageVersionModel.created_at.asc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_latest_package_version_by_package_id(self, package_id: str) -> PackageVersionModel | None:
        result = await self.session.execute(
            select(PackageVersionModel)
            .options(
                selectinload(PackageVersionModel.documents),
                selectinload(PackageVersionModel.issues),
            )
            .where(PackageVersionModel.package_id == package_id)
            .order_by(PackageVersionModel.version.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()


class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_many(self, package_version_id: str, documents: list[dict]) -> list[DocumentModel]:
        items = []
        for document in documents:
            item = DocumentModel(
                package_version_id=package_version_id,
                filename=document["filename"],
                filepath=document["filepath"],
                detected_type=document.get("detected_type"),
                size=document["size"],
            )
            items.append(item)
        self.session.add_all(items)
        await self.session.flush()
        return items


class IssueRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_many(self, package_version_id: str, issues: list[dict]) -> list[IssueModel]:
        items = []
        for issue in issues:
            item = IssueModel(
                package_version_id=package_version_id,
                level=issue["level"],
                message=issue["message"],
            )
            items.append(item)
        self.session.add_all(items)
        await self.session.flush()
        return items
