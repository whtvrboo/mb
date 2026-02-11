"""Documents module ORM models."""

from datetime import datetime

from sqlalchemy import JSON, BigInteger, CheckConstraint, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mitlist.db.base import BaseModel, TimestampMixin


class CredentialType(str):
    """Credential types."""

    WIFI = "WIFI"
    STREAMING = "STREAMING"
    BANK = "BANK"
    UTILITY = "UTILITY"
    OTHER = "OTHER"


class AccessLevel(str):
    """Access levels."""

    ADMIN_ONLY = "ADMIN_ONLY"
    MEMBER = "MEMBER"
    GUEST = "GUEST"


class Document(BaseModel, TimestampMixin):
    """Document - file storage record."""

    __tablename__ = "documents"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False, index=True)
    uploaded_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    file_key: Mapped[str] = mapped_column(String(500), nullable=False)  # S3 key
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    folder_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    tags: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_encrypted: Mapped[bool] = mapped_column(default=False, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # Relationships
    shares: Mapped[list["DocumentShare"]] = relationship(
        "DocumentShare", back_populates="document", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("file_size_bytes >= 0", name="ck_document_size_non_negative"),
    )


class DocumentShare(BaseModel, TimestampMixin):
    """Document share - share document with specific user."""

    __tablename__ = "document_shares"

    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), nullable=False, index=True)
    shared_with_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    can_edit: Mapped[bool] = mapped_column(default=False, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="shares")


class SharedCredential(BaseModel, TimestampMixin):
    """Shared credential - encrypted passwords and credentials."""

    __tablename__ = "shared_credentials"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    credential_type: Mapped[str] = mapped_column(String(50), nullable=False)
    username_identity: Mapped[str | None] = mapped_column(String(255), nullable=True)
    encrypted_password: Mapped[str] = mapped_column(String(500), nullable=False)
    access_level: Mapped[str] = mapped_column(String(20), nullable=False)
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    last_rotated_at: Mapped[datetime | None] = mapped_column(nullable=True)
    rotation_reminder_days: Mapped[int | None] = mapped_column(nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
