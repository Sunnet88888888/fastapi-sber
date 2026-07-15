import asyncio
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

from fastapi import UploadFile
from starlette.datastructures import Headers

from app.services.check_document import detect_document_type
from app.services.package_service import PackageService


def create_upload_file(filename: str, content: bytes = b"dummy") -> UploadFile:
    headers = Headers({"content-type": "application/pdf"})
    return UploadFile(file=BytesIO(content), filename=filename, headers=headers)


def make_dummy_version() -> SimpleNamespace:
    return SimpleNamespace(
        id="version-1",
        package_id="package-1",
        version=1,
        program="federal",
        status="check_in_progress",
        status_label="Проверка начата",
        reason=None,
        extracted=None,
        checked_at=None,
    )


def patch_service_for_create(service: PackageService, monkeypatch) -> None:
    async def fake_save_file(self, package_id: str, version: int, file: UploadFile) -> Path:
        return Path("/tmp/fake-path")

    async def fake_get_file_size(self, file: UploadFile) -> int:
        return len(await file.read())

    async def fake_commit():
        return None

    async def fake_create_many(*args, **kwargs):
        return []

    async def fake_get_or_create_package(self, package_id: str | None):
        return "package-1", 1

    dummy_version = make_dummy_version()

    async def fake_version_create(package_id, version, program, status, status_label, reason):
        return dummy_version

    dummy_db = SimpleNamespace(commit=fake_commit)
    service.db = dummy_db

    monkeypatch.setattr(service, "_save_file", fake_save_file.__get__(service, PackageService))
    monkeypatch.setattr(service, "_get_file_size", fake_get_file_size.__get__(service, PackageService))
    monkeypatch.setattr(service, "_get_or_create_package", fake_get_or_create_package.__get__(service, PackageService))
    monkeypatch.setattr(service.version_repo, "create", fake_version_create)
    monkeypatch.setattr(service.issue_repo, "create_many", fake_create_many)
    monkeypatch.setattr(service.document_repo, "create_many", fake_create_many)


def test_detect_document_type_contract():
    detected_type, warning = detect_document_type("Договор_с_контрагентом.pdf")
    assert detected_type == "contract"
    assert warning is None


def test_detect_document_type_invoice_with_ё():
    detected_type, warning = detect_document_type("счёт_за_услуги.docx")
    assert detected_type == "invoice"
    assert warning is None


def test_detect_document_type_unknown_returns_warning():
    filename = "unknown-document.pdf"
    detected_type, warning = detect_document_type(filename)
    assert detected_type is None
    assert warning is not None
    assert warning["level"] == "warning"
    assert filename in warning["message"]


def test_create_package_version_all_required_documents_keeps_check_in_progress(monkeypatch):
    service = PackageService(db=None)
    patch_service_for_create(service, monkeypatch)

    async def fake_file_type_error(file):
        return None

    async def fake_file_size_error(file):
        return None

    def fake_detect_document_type(filename):
        if "contract" in filename:
            return "contract", None
        if "specification" in filename:
            return "specification", None
        if "invoice" in filename:
            return "invoice", None
        if "act" in filename:
            return "act", None
        return None, {"level": "warning", "message": "unknown"}

    monkeypatch.setattr("app.services.package_service.file_type_error", fake_file_type_error)
    monkeypatch.setattr("app.services.package_service.file_size_error", fake_file_size_error)
    monkeypatch.setattr("app.services.package_service.detect_document_type", fake_detect_document_type)

    files = [
        create_upload_file("contract.pdf"),
        create_upload_file("specification.pdf"),
        create_upload_file("invoice.pdf"),
        create_upload_file("act.pdf"),
    ]

    response = asyncio.run(service.create_package_version(files=files, program="federal"))

    assert response["status"] == "check_in_progress"
    assert response["status_label"] == "Проверка начата"
    assert response["reason"] is None
    assert all(issue["level"] != "error" for issue in response["issues"])


def test_create_package_version_invalid_file_type_rejects_package(monkeypatch):
    service = PackageService(db=None)
    patch_service_for_create(service, monkeypatch)

    async def fake_file_type_error(file):
        if file.filename == "contract.pdf":
            return {"level": "error", "message": "Недопустимый формат файла - application/msword"}
        return None

    async def fake_file_size_error(file):
        return None

    def fake_detect_document_type(filename):
        if "contract" in filename:
            return "contract", None
        if "specification" in filename:
            return "specification", None
        if "invoice" in filename:
            return "invoice", None
        if "act" in filename:
            return "act", None
        return None, {"level": "warning", "message": "unknown"}

    monkeypatch.setattr("app.services.package_service.file_type_error", fake_file_type_error)
    monkeypatch.setattr("app.services.package_service.file_size_error", fake_file_size_error)
    monkeypatch.setattr("app.services.package_service.detect_document_type", fake_detect_document_type)

    files = [
        create_upload_file("contract.pdf"),
        create_upload_file("specification.pdf"),
        create_upload_file("invoice.pdf"),
        create_upload_file("act.pdf"),
    ]

    response = asyncio.run(service.create_package_version(files=files, program="federal"))

    assert response["status"] == "rejected"
    assert response["reason"] is not None
    assert "Недопустимый формат файла" in response["reason"]
    assert any(issue["level"] == "error" for issue in response["issues"])


def test_create_package_version_missing_required_document_rejects_package(monkeypatch):
    service = PackageService(db=None)
    patch_service_for_create(service, monkeypatch)

    async def fake_file_type_error(file):
        return None

    async def fake_file_size_error(file):
        return None

    def fake_detect_document_type(filename):
        if "contract" in filename:
            return "contract", None
        if "invoice" in filename:
            return "invoice", None
        return None, {"level": "warning", "message": "Не удалось определить тип документа"}

    monkeypatch.setattr("app.services.package_service.file_type_error", fake_file_type_error)
    monkeypatch.setattr("app.services.package_service.file_size_error", fake_file_size_error)
    monkeypatch.setattr("app.services.package_service.detect_document_type", fake_detect_document_type)

    files = [
        create_upload_file("contract.pdf"),
        create_upload_file("invoice.pdf"),
    ]

    response = asyncio.run(service.create_package_version(files=files, program="federal"))

    assert response["status"] == "rejected"
    assert response["reason"] is not None
    assert "Отсутствует обязательный документ" in response["reason"]
    assert any(issue["level"] == "error" for issue in response["issues"])
