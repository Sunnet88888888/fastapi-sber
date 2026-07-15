from pydantic import BaseModel, Field, ConfigDict, EmailStr
from decimal import Decimal
from datetime import datetime
from uuid import UUID


class UserCreate(BaseModel):
    email: EmailStr = Field(description="E-mail of the user")
    password: str = Field(
        min_length=8, description="minimal character number for password is 8"
    )

class User(BaseModel):
    id: UUID
    email: EmailStr
    is_active: bool
    role: str
    model_config = ConfigDict(from_attributes=True)
    
  
  
class SuperUser(BaseModel):
    email: EmailStr = Field(description="E-mail of superuser. Get email from .env")
    password: str = Field(min_length=8, description="Minimal character number for password is 8. Get password from .env")  
    new_admin_email: EmailStr = Field(description="Email of new admin")
    new_admin_password: str = Field(description="New admin password")
  
  
    
class RefreshTokenRequest(BaseModel):
    refresh_token: str
    
    
    
class IssueItem(BaseModel):
    level: str
    message: str


class DocumentItem(BaseModel):
    filename: str
    detected_type: str | None
    size: int


class CheckResponse(BaseModel):
    package_id: str
    package_version_id: UUID
    version: int
    program: str
    status: str
    status_label: str
    reason: str | None
    issues: list[IssueItem]
    documents: list[DocumentItem]
    extracted: dict | None
    checked_at: datetime | None


class CheckListItem(BaseModel):
    package_id: str
    package_version_ids: list[str]
    date: datetime
    program: str
    status: str
    document_count: int




class AIUncheckedPackageResponse(BaseModel):
    package_id: str


class AIDocumentItem(BaseModel):
    filename: str
    detected_type: str | None
    size: int
    content_base64: str


class AIPackageDocumentsResponse(BaseModel):
    package_id: str
    package_version_id: UUID
    version: int
    program: str
    status: str
    documents: list[AIDocumentItem]
    

class AICheckResult(BaseModel):
    extracted: dict
    checked_at: datetime | None = None
    status: str | None = None
    status_label: str | None = None
    reason: str | None = None
    