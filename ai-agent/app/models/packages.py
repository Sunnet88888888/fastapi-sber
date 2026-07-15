import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PackageModel(Base):
    __tablename__ = "packages"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    current_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    versions: Mapped[list["PackageVersionModel"]] = relationship(
        "PackageVersionModel",
        back_populates="package",
        order_by="PackageVersionModel.version",
        cascade="all, delete-orphan",
    )
