from typing import Optional
import uuid
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class DocumentModel(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    package_version_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("package_versions.id"), nullable=False
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    filepath: Mapped[str] = mapped_column(String(1024), nullable=False)
    detected_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    size: Mapped[int] = mapped_column(Integer, nullable=False)

    package_version: Mapped["PackageVersionModel"] = relationship(
        "PackageVersionModel", back_populates="documents"
    )