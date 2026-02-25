"""Documents module service layer. PRIVATE - other modules import from interface.py."""

import base64
import hashlib
import logging
import re
import secrets
import unicodedata
from datetime import UTC, datetime

from cryptography.fernet import Fernet
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.core.config import settings
from mitlist.core.errors import ForbiddenError, NotFoundError
from mitlist.modules.documents.models import Document, SharedCredential


# ---------- Documents ----------
async def list_documents(
    db: AsyncSession,
    group_id: int,
    folder_path: str | None = None,
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


async def get_document_by_id(db: AsyncSession, document_id: int) -> Document | None:
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
    folder_path: str | None = None,
    tags: dict | None = None,
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
    doc.deleted_at = datetime.now(UTC)
    await db.flush()


def _sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to be safe for storage.

    - Normalizes unicode characters
    - Removes non-alphanumeric characters except (.-_)
    - Prevents path traversal (..)
    - Truncates to reasonable length
    """
    # Normalize unicode characters (NFKD)
    filename = unicodedata.normalize("NFKD", filename)

    # Encode to ASCII, ignoring errors, then decode back to string
    filename = filename.encode("ascii", "ignore").decode("ascii")

    # Replace anything that isn't alphanumeric, dot, dash, or underscore with underscore
    # This effectively removes slashes (forward and backward) and control chars
    filename = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)

    # Remove multiple underscores
    filename = re.sub(r"_+", "_", filename)

    # Strip leading/trailing dots and underscores
    filename = filename.strip("._")

    # Ensure it's not empty
    if not filename:
        filename = "unnamed_file"

    return filename


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
    timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    random_suffix = secrets.token_hex(8)
    safe_name = _sanitize_filename(file_name)
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


async def get_credential_by_id(db: AsyncSession, credential_id: int) -> SharedCredential | None:
    """Get a credential by ID."""
    result = await db.execute(select(SharedCredential).where(SharedCredential.id == credential_id))
    return result.scalar_one_or_none()


async def create_credential(
    db: AsyncSession,
    group_id: int,
    name: str,
    credential_type: str,
    password: str,
    access_level: str,
    username_identity: str | None = None,
    url: str | None = None,
    rotation_reminder_days: int | None = None,
    notes: str | None = None,
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
        last_rotated_at=datetime.now(UTC),
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
        raise NotFoundError(
            code="CREDENTIAL_NOT_FOUND", detail=f"Credential {credential_id} not found"
        )

    # Check access level
    if cred.access_level == "ADMIN_ONLY" and user_role != "ADMIN":
        raise ForbiddenError(
            code="ACCESS_DENIED", detail="Admin access required for this credential"
        )

    decrypted = _decrypt_password(cred.encrypted_password)
    return cred, decrypted


async def delete_credential(db: AsyncSession, credential_id: int) -> None:
    """Delete a credential."""
    cred = await get_credential_by_id(db, credential_id)
    if not cred:
        raise NotFoundError(
            code="CREDENTIAL_NOT_FOUND", detail=f"Credential {credential_id} not found"
        )
    await db.delete(cred)
    await db.flush()


# ---------- Encryption helpers ----------
def _get_fernet() -> Fernet:
    """Derive a valid Fernet key from SECRET_KEY."""
    # Fernet requires a 32-byte url-safe base64-encoded key
    # We hash the SECRET_KEY to 32 bytes (SHA256) and then url-safe base64 encode it
    key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    key_b64 = base64.urlsafe_b64encode(key)
    return Fernet(key_b64)


def _encrypt_password(password: str) -> str:
    """Encrypt password using Fernet (AES-128-CBC + HMAC)."""
    f = _get_fernet()
    return f.encrypt(password.encode()).decode()


def _decrypt_password(encrypted: str) -> str:
    """Decrypt password using Fernet, falling back to Base64 for legacy data."""
    # Fernet tokens (version 128) start with gAAAA
    if encrypted.startswith("gAAAA"):
        f = _get_fernet()
        # If this fails (InvalidToken), we want it to raise, not fallback
        return f.decrypt(encrypted.encode()).decode()

    # Fallback to base64 (legacy) if not a Fernet token
    # This allows reading existing data that hasn't been re-encrypted yet
    try:
        logging.getLogger(__name__).warning("Legacy Base64 password access detected.")
        return base64.b64decode(encrypted.encode()).decode()
    except Exception as e:
        raise ValueError("Failed to decrypt password") from e
