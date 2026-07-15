import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Integer, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PackageVersionModel(Base):
    __tablename__ = "package_versions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    package_id: Mapped[str] = mapped_column(String(36), ForeignKey("packages.id"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    program: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    status_label: Mapped[str] = mapped_column(String(255), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    extracted: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    package: Mapped["PackageModel"] = relationship(
        "PackageModel", back_populates="versions"
    )
    documents: Mapped[list["DocumentModel"]] = relationship(
        "DocumentModel", back_populates="package_version",
        cascade="all, delete-orphan",
    )
    issues: Mapped[list["IssueModel"]] = relationship(
        "IssueModel", back_populates="package_version",
        cascade="all, delete-orphan",
    )
