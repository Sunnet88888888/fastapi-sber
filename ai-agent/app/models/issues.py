import uuid

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class IssueModel(Base):
    __tablename__ = "issues"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    package_version_id: Mapped[str] = mapped_column(String(36), ForeignKey("package_versions.id"), nullable=False)
    level: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(String(2048), nullable=False)

    package_version: Mapped["PackageVersionModel"] = relationship(
        "PackageVersionModel", back_populates="issues"
    )
