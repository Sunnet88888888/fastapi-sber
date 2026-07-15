import base64
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.package_repository import (
    PackageRepository,
    PackageVersionRepository,
    DocumentRepository,
    IssueRepository,
)
from app.services.check_document import (
    detect_document_type,
    file_type_error,
    file_size_error,
)


ALLOWED_PROGRAMS = {
    "federal": {"contract", "specification", "invoice", "act"},
    "regional": {"contract", "invoice", "act"},
}

STATUS_LABELS = {
    "check_in_progress": "Проверка начата",
    "approved": "Пакет одобрен",
    "rejected": "Нельзя заявлять в банк",
}

BASE_STORAGE_PATH = Path("./storage")
BASE_STORAGE_PATH.mkdir(parents=True, exist_ok=True)


class PackageService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.package_repo = PackageRepository(db)
        self.version_repo = PackageVersionRepository(db)
        self.document_repo = DocumentRepository(db)
        self.issue_repo = IssueRepository(db)

    async def list_checks(self) -> list[dict]:
        raw_checks = await self.version_repo.list_checks()
        grouped: dict[str, dict[str, Any]] = {}
        for row in raw_checks:
            package_id = row["package_id"]
            version_id = row["package_version_id"]
            if package_id not in grouped:
                grouped[package_id] = {
                    "package_id": package_id,
                    "package_version_ids": [version_id],
                    "latest_created_at": row["created_at"],
                    "latest_program": row["program"],
                    "latest_status": row["status"],
                    "document_count": row["document_count"],
                }
            else:
                grouped[package_id]["package_version_ids"].append(version_id)
        return list(grouped.values())

    async def get_check_by_id(self, package_version_id: str) -> dict[str, Any]:
        package_version = await self.version_repo.get_check_by_id(package_version_id)
        if package_version is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Check not found")

        return {
            "package_id": package_version.package_id,
            "package_version_id": package_version.id,
            "version": package_version.version,
            "program": package_version.program,
            "status": package_version.status,
            "status_label": package_version.status_label,
            "reason": package_version.reason,
            "issues": [
                {"level": issue.level, "message": issue.message}
                for issue in package_version.issues
            ],
            "documents": [
                {
                    "filename": document.filename,
                    "detected_type": document.detected_type,
                    "size": document.size,
                }
                for document in package_version.documents
            ],
            "extracted": package_version.extracted,
            "checked_at": package_version.checked_at,
        }

    async def get_next_unchecked_package_id(self) -> str | None:
        package_id = await self.version_repo.get_earliest_unchecked_package_id()
        if package_id is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No unchecked package found")
        return package_id

    async def get_package_documents(self, package_id: str) -> dict[str, Any]:
        package_version = await self.version_repo.get_latest_package_version_by_package_id(package_id)
        if package_version is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Package not found")

        documents = []
        for document in package_version.documents:
            try:
                file_path = Path(document.filepath)
                content = file_path.read_bytes()
                encoded = base64.b64encode(content).decode("ascii")
            except Exception:
                encoded = ""

            documents.append(
                {
                    "filename": document.filename,
                    "detected_type": document.detected_type,
                    "size": document.size,
                    "content_base64": encoded,
                }
            )

        return {
            "package_id": package_id,
            "package_version_id": package_version.id,
            "version": package_version.version,
            "program": package_version.program,
            "status": package_version.status,
            "documents": documents,
        }

    async def accept_checked_package(self, package_id: str, result: dict[str, Any]) -> dict[str, Any]:
        # Find the latest package version for this package (prefer in-progress)
        package_version = await self.version_repo.get_latest_package_version_by_package_id(package_id)
        if package_version is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Package not found")

        # If client provided checked_at use it, otherwise set now
        checked_at = result.get("checked_at")
        if checked_at is None:
            checked_at = datetime.now(timezone.utc)

        # Update extracted and metadata
        package_version.extracted = result.get("extracted")
        package_version.checked_at = checked_at

        # Optional status update
        status_val = result.get("status")
        if status_val:
            package_version.status = status_val
        status_label = result.get("status_label")
        if status_label:
            package_version.status_label = status_label
        reason = result.get("reason")
        if reason:
            package_version.reason = reason

        await self.db.commit()

        return {
            "package_id": package_version.package_id,
            "package_version_id": package_version.id,
            "version": package_version.version,
            "program": package_version.program,
            "status": package_version.status,
            "status_label": package_version.status_label,
            "reason": package_version.reason,
            "extracted": package_version.extracted,
            "checked_at": package_version.checked_at,
        }

    async def _get_or_create_package(self, package_id: str | None) -> tuple[str, int]:
        if package_id is None:
            package = await self.package_repo.create()
            return package.id, 1

        package = await self.package_repo.get_by_id(package_id)
        if package is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect id of package")
           ## package = await self.package_repo.create()
           # return package.id, 1

        package.current_version += 1
        await self.db.flush()
        return package.id, package.current_version

    async def create_package_version(
        self,
        files: list[UploadFile],
        program: str,
        package_id: str | None = None,
        created_by: str | None = None,
    ) -> dict[str, Any]:
        if program not in ALLOWED_PROGRAMS:
            raise ValueError(f"Unsupported program: {program}")

        package_id, version = await self._get_or_create_package(package_id)

        package_version = await self.version_repo.create(
            package_id=package_id,
            version=version,
            program=program,
            status="check_in_progress",
            status_label=STATUS_LABELS["check_in_progress"],
            reason=None,
        )

        document_records = []
        all_issues = []
        detected_types = set()

        for upload_file in files:
            validation_issue = await file_type_error(upload_file)
            if validation_issue:
                all_issues.append(validation_issue)

            size_issue = await file_size_error(upload_file)
            if size_issue:
                all_issues.append(size_issue)

            detected_type, warning_issue = detect_document_type(upload_file.filename)
            if warning_issue:
                all_issues.append(warning_issue)
            if detected_type is not None:
                detected_types.add(detected_type)

            file_path = await self._save_file(package_id, version, upload_file)
            document_records.append(
                {
                    "filename": upload_file.filename,
                    "filepath": str(file_path),
                    "detected_type": detected_type,
                    "size": await self._get_file_size(upload_file),
                }
            )

        # Required document validation
        for required_doc in ALLOWED_PROGRAMS[program]:
            if required_doc not in detected_types:
                all_issues.append(
                    {
                        "level": "error",
                        "message": f"Отсутствует обязательный документ: {required_doc}",
                    }
                )

        # Determine final status
        has_errors = any(issue["level"] == "error" for issue in all_issues)
        status = "rejected" if has_errors else "check_in_progress"
        status_label = STATUS_LABELS[status]
        reason = None
        if has_errors:
            reason = " ".join(issue["message"] for issue in all_issues if issue["level"] == "error")

        package_version.status = status
        package_version.status_label = status_label
        package_version.reason = reason

        await self.issue_repo.create_many(package_version.id, all_issues)
        await self.document_repo.create_many(package_version.id, document_records)
        await self.db.commit()

        response = {
            "package_id": package_id,
            "package_version_id": package_version.id,
            "version": version,
            "status": status,
            "status_label": status_label,
            "reason": reason,
            "issues": all_issues,
            "documents": [
                {
                    "filename": item["filename"],
                    "detected_type": item["detected_type"],
                    "size": item["size"],
                }
                for item in document_records
            ],
            "extracted": None,
            "checked_at": package_version.checked_at,
        }
        return response

    async def _save_file(self, package_id: str, version: int, file: UploadFile) -> Path:
        package_folder = BASE_STORAGE_PATH / package_id / f"v{version}"
        package_folder.mkdir(parents=True, exist_ok=True)
        file_path = package_folder / file.filename
        content = await file.read()
        file_path.write_bytes(content)
        await file.seek(0)
        return file_path

    async def _get_file_size(self, file: UploadFile) -> int:
        content = await file.read()
        await file.seek(0)
        return len(content)
