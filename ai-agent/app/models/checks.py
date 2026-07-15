from typing import List
from sqlalchemy import Boolean, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import uuid
from datetime import datetime, timezone

class CheckModel(Base):
    __tablename__ = "checks"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())  
    )
    program: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    status_label: Mapped[str] = mapped_column(String, nullable=False)
    reason: Mapped[str] = mapped_column(String, nullable = True)
    issues: Mapped[dict] = mapped_column(String, nullable = True)
    version: Mapped[int] = mapped_column(Integer, nullable = False)
    url: Mapped[str] = mapped_column(String, nullable = False)
    
    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default = lambda: datetime.now(timezone.utc)
    )
    
    documents: Mapped[List["DocumentModel"]] = relationship(
        "DocumentModel",
        back_populates="check",
    )