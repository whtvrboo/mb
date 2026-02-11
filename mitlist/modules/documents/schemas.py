"""Documents module Pydantic schemas for request/response models."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ====================
# Document Schemas
# ====================
class DocumentBase(BaseModel):
    """Base document schema."""

    file_name: str = Field(..., min_length=1, max_length=255)
    mime_type: str = Field(..., max_length=100)
    folder_path: str | None = Field(None, max_length=500)
    tags: dict[str, Any] | None = None
    is_encrypted: bool = False


class DocumentCreate(DocumentBase):
    """Schema for creating a document (metadata only, file uploaded separately)."""

    group_id: int
    file_key: str = Field(..., max_length=500)  # S3 key
    file_size_bytes: int = Field(..., ge=0)


class DocumentUpdate(BaseModel):
    """Schema for updating a document."""

    file_name: str | None = Field(None, min_length=1, max_length=255)
    folder_path: str | None = Field(None, max_length=500)
    tags: dict[str, Any] | None = None


class DocumentResponse(DocumentBase):
    """Schema for document response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    uploaded_by_id: int
    file_key: str
    file_size_bytes: int
    created_at: datetime
    updated_at: datetime


class DocumentUploadRequest(BaseModel):
    """Schema for requesting a presigned upload URL."""

    group_id: int
    file_name: str = Field(..., min_length=1, max_length=255)
    mime_type: str = Field(..., max_length=100)
    file_size_bytes: int = Field(..., ge=0)
    folder_path: str | None = Field(None, max_length=500)


class DocumentUploadResponse(BaseModel):
    """Schema for presigned upload URL response."""

    upload_url: str
    file_key: str
    expires_in_seconds: int


class DocumentDownloadResponse(BaseModel):
    """Schema for presigned download URL response."""

    download_url: str
    expires_in_seconds: int


# ====================
# DocumentShare Schemas
# ====================
class DocumentShareBase(BaseModel):
    """Base document share schema."""

    can_edit: bool = False
    expires_at: datetime | None = None


class DocumentShareCreate(DocumentShareBase):
    """Schema for creating a document share."""

    document_id: int
    shared_with_user_id: int


class DocumentShareUpdate(BaseModel):
    """Schema for updating a document share."""

    can_edit: bool | None = None
    expires_at: datetime | None = None


class DocumentShareResponse(DocumentShareBase):
    """Schema for document share response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    document_id: int
    shared_with_user_id: int
    created_at: datetime
    updated_at: datetime


# ====================
# SharedCredential Schemas
# ====================
class SharedCredentialBase(BaseModel):
    """Base shared credential schema."""

    name: str = Field(..., min_length=1, max_length=255)
    credential_type: str = Field(..., pattern="^(WIFI|STREAMING|BANK|UTILITY|OTHER)$")
    username_identity: str | None = Field(None, max_length=255)
    access_level: str = Field(..., pattern="^(ADMIN_ONLY|MEMBER|GUEST)$")
    url: str | None = Field(None, max_length=500)
    rotation_reminder_days: int | None = Field(None, ge=1)
    notes: str | None = Field(None, max_length=1000)


class SharedCredentialCreate(SharedCredentialBase):
    """Schema for creating a shared credential."""

    group_id: int
    password: str = Field(..., min_length=1)  # Will be encrypted


class SharedCredentialUpdate(BaseModel):
    """Schema for updating a shared credential."""

    name: str | None = Field(None, min_length=1, max_length=255)
    credential_type: str | None = Field(None, pattern="^(WIFI|STREAMING|BANK|UTILITY|OTHER)$")
    username_identity: str | None = Field(None, max_length=255)
    access_level: str | None = Field(None, pattern="^(ADMIN_ONLY|MEMBER|GUEST)$")
    url: str | None = Field(None, max_length=500)
    rotation_reminder_days: int | None = Field(None, ge=1)
    notes: str | None = Field(None, max_length=1000)


class SharedCredentialPasswordUpdate(BaseModel):
    """Schema for updating credential password (rotation)."""

    password: str = Field(..., min_length=1)


class SharedCredentialResponse(SharedCredentialBase):
    """Schema for shared credential response (without password)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    last_rotated_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class SharedCredentialWithPasswordResponse(SharedCredentialResponse):
    """Schema for shared credential with decrypted password."""

    decrypted_password: str


# ====================
# Aggregation/Summary Schemas
# ====================
class FolderContentsResponse(BaseModel):
    """Schema for folder contents."""

    folder_path: str
    documents: list[DocumentResponse]
    subfolders: list[str]
    total_size_bytes: int


class DocumentSearchRequest(BaseModel):
    """Schema for document search."""

    group_id: int
    query: str | None = Field(None, max_length=255)
    folder_path: str | None = Field(None, max_length=500)
    mime_types: list[str] | None = Field(None, max_length=20)
    tags: dict[str, Any] | None = None
    uploaded_by_id: int | None = None
    created_after: datetime | None = None
    created_before: datetime | None = None


class CredentialRotationReminderResponse(BaseModel):
    """Schema for credential rotation reminder."""

    credential_id: int
    credential_name: str
    credential_type: str
    last_rotated_at: datetime | None = None
    rotation_reminder_days: int
    days_since_rotation: int
    is_overdue: bool


class GroupStorageSummaryResponse(BaseModel):
    """Schema for group storage summary."""

    group_id: int
    total_documents: int
    total_size_bytes: int
    documents_by_type: dict[str, int]  # mime_type -> count
    recent_uploads: list[DocumentResponse]
    shared_credentials_count: int
