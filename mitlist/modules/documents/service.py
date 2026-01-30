"""Documents module service layer. PRIVATE - other modules import from interface.py."""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.core.errors import ForbiddenError, NotFoundError
from mitlist.modules.documents.models import Document, DocumentShare, SharedCredential


# ---------- Documents ----------
async def list_documents(
    db: AsyncSession,
    group_id: int,
    folder_path: Optional[str] = None,
) -> list[Document]:
    """List documents for a group, optionally filtered by folder."""
    q = select(Document).where(
        Document.group_id == group_id,
        Document.deleted_at.is_(None),
    )
    if folder_path is not None:
        q = q.where(Document.folder_path == folder_path)
    q = q.order_by(Document.created_at.desc())
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_document_by_id(db: AsyncSession, document_id: int) -> Optional[Document]:
    """Get a document by ID."""
    result = await db.execute(
        select(Document).where(Document.id == document_id, Document.deleted_at.is_(None))
    )
    return result.scalar_one_or_none()


async def create_document(
    db: AsyncSession,
    group_id: int,
    uploaded_by_id: int,
    file_name: str,
    file_key: str,
    mime_type: str,
    file_size_bytes: int,
    folder_path: Optional[str] = None,
    tags: Optional[dict] = None,
    is_encrypted: bool = False,
) -> Document:
    """Create a document record."""
    doc = Document(
        group_id=group_id,
        uploaded_by_id=uploaded_by_id,
        file_name=file_name,
        file_key=file_key,
        mime_type=mime_type,
        file_size_bytes=file_size_bytes,
        folder_path=folder_path,
        tags=tags,
        is_encrypted=is_encrypted,
    )
    db.add(doc)
    await db.flush()
    await db.refresh(doc)
    return doc


async def delete_document(db: AsyncSession, document_id: int) -> None:
    """Soft delete a document."""
    doc = await get_document_by_id(db, document_id)
    if not doc:
        raise NotFoundError(code="DOCUMENT_NOT_FOUND", detail=f"Document {document_id} not found")
    doc.deleted_at = datetime.now(timezone.utc)
    await db.flush()


def generate_presigned_upload_url(
    group_id: int,
    file_name: str,
    mime_type: str,
    file_size_bytes: int,
) -> tuple[str, str, int]:
    """
    Generate a presigned URL for uploading a file.

    In a real implementation, this would use S3/MinIO SDK.
    Returns (upload_url, file_key, expires_in_seconds).
    """
    # Generate a unique file key
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    random_suffix = secrets.token_hex(8)
    safe_name = file_name.replace(" ", "_").replace("/", "_")
    file_key = f"groups/{group_id}/documents/{timestamp}_{random_suffix}_{safe_name}"

    # In production, use boto3 or minio client to generate presigned URL
    expires_in_seconds = 3600  # 1 hour
    upload_url = f"/api/v1/documents/upload-target?key={file_key}"

    return upload_url, file_key, expires_in_seconds


def generate_presigned_download_url(file_key: str) -> tuple[str, int]:
    """
    Generate a presigned URL for downloading a file.

    In a real implementation, this would use S3/MinIO SDK.
    Returns (download_url, expires_in_seconds).
    """
    expires_in_seconds = 3600  # 1 hour
    download_url = f"/api/v1/documents/download-target?key={file_key}"

    return download_url, expires_in_seconds


# ---------- Shared Credentials ----------
async def list_credentials(db: AsyncSession, group_id: int) -> list[SharedCredential]:
    """List shared credentials for a group."""
    result = await db.execute(
        select(SharedCredential)
        .where(SharedCredential.group_id == group_id)
        .order_by(SharedCredential.name)
    )
    return list(result.scalars().all())


async def get_credential_by_id(db: AsyncSession, credential_id: int) -> Optional[SharedCredential]:
    """Get a credential by ID."""
    result = await db.execute(
        select(SharedCredential).where(SharedCredential.id == credential_id)
    )
    return result.scalar_one_or_none()


async def create_credential(
    db: AsyncSession,
    group_id: int,
    name: str,
    credential_type: str,
    password: str,
    access_level: str,
    username_identity: Optional[str] = None,
    url: Optional[str] = None,
    rotation_reminder_days: Optional[int] = None,
    notes: Optional[str] = None,
) -> SharedCredential:
    """Create a shared credential with encrypted password."""
    # In production, use proper encryption (e.g., cryptography.fernet, age, or vault)
    encrypted_password = _encrypt_password(password)

    cred = SharedCredential(
        group_id=group_id,
        name=name,
        credential_type=credential_type,
        encrypted_password=encrypted_password,
        access_level=access_level,
        username_identity=username_identity,
        url=url,
        rotation_reminder_days=rotation_reminder_days,
        notes=notes,
        last_rotated_at=datetime.now(timezone.utc),
    )
    db.add(cred)
    await db.flush()
    await db.refresh(cred)
    return cred


async def reveal_credential(
    db: AsyncSession,
    credential_id: int,
    user_id: int,
    user_role: str,
) -> tuple[SharedCredential, str]:
    """
    Reveal a credential's password.

    Returns the credential and decrypted password.
    Checks access level against user role.
    """
    cred = await get_credential_by_id(db, credential_id)
    if not cred:
        raise NotFoundError(code="CREDENTIAL_NOT_FOUND", detail=f"Credential {credential_id} not found")

    # Check access level
    if cred.access_level == "ADMIN_ONLY" and user_role != "ADMIN":
        raise ForbiddenError(code="ACCESS_DENIED", detail="Admin access required for this credential")

    decrypted = _decrypt_password(cred.encrypted_password)
    return cred, decrypted


async def delete_credential(db: AsyncSession, credential_id: int) -> None:
    """Delete a credential."""
    cred = await get_credential_by_id(db, credential_id)
    if not cred:
        raise NotFoundError(code="CREDENTIAL_NOT_FOUND", detail=f"Credential {credential_id} not found")
    await db.delete(cred)
    await db.flush()


# ---------- Encryption helpers (replace with Fernet/vault in production) ----------
def _encrypt_password(password: str) -> str:
    """Encode password for storage. In production use cryptography.fernet or vault."""
    import base64
    return base64.b64encode(password.encode()).decode()


def _decrypt_password(encrypted: str) -> str:
    """Decode stored password. In production use cryptography.fernet or vault."""
    import base64
    return base64.b64decode(encrypted.encode()).decode()
