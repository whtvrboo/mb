"""Documents & Files module FastAPI router. Handles /documents and /credentials."""


from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api.deps import (
    get_current_group_id,
    get_current_user,
    get_db,
    require_introspection_user,
)
from mitlist.core.errors import NotFoundError
from mitlist.modules.auth.interface import require_member
from mitlist.modules.auth.models import User
from mitlist.modules.documents import schemas, service

router = APIRouter(tags=["documents", "credentials"])


@router.get("/documents", response_model=list[schemas.DocumentResponse])
async def get_documents(
    group_id: int = Depends(get_current_group_id),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List documents for the current group."""
    await require_member(db, group_id, user.id)
    docs = await service.list_documents(db, group_id)
    return [schemas.DocumentResponse.model_validate(d) for d in docs]


@router.post("/documents/upload", response_model=schemas.DocumentUploadResponse)
async def post_documents_upload(
    data: schemas.DocumentUploadRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a presigned URL for uploading a document."""
    await require_member(db, data.group_id, user.id)

    upload_url, file_key, expires_in = service.generate_presigned_upload_url(
        group_id=data.group_id,
        file_name=data.file_name,
        mime_type=data.mime_type,
        file_size_bytes=data.file_size_bytes,
    )

    # Create the document record (pending upload)
    await service.create_document(
        db,
        group_id=data.group_id,
        uploaded_by_id=user.id,
        file_name=data.file_name,
        file_key=file_key,
        mime_type=data.mime_type,
        file_size_bytes=data.file_size_bytes,
        folder_path=data.folder_path,
    )

    return schemas.DocumentUploadResponse(
        upload_url=upload_url,
        file_key=file_key,
        expires_in_seconds=expires_in,
    )


@router.get("/documents/{document_id}/download", response_model=schemas.DocumentDownloadResponse)
async def get_documents_download(
    document_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a presigned URL for downloading a document."""
    doc = await service.get_document_by_id(db, document_id)
    if not doc:
        raise NotFoundError(code="DOCUMENT_NOT_FOUND", detail=f"Document {document_id} not found")

    await require_member(db, doc.group_id, user.id)

    download_url, expires_in = service.generate_presigned_download_url(doc.file_key)

    return schemas.DocumentDownloadResponse(
        download_url=download_url,
        expires_in_seconds=expires_in,
    )


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a document (soft delete)."""
    doc = await service.get_document_by_id(db, document_id)
    if not doc:
        raise NotFoundError(code="DOCUMENT_NOT_FOUND", detail=f"Document {document_id} not found")

    # Only uploader or admin can delete
    if doc.uploaded_by_id != user.id:
        from mitlist.modules.auth.interface import require_admin

        await require_admin(db, doc.group_id, user.id)

    await service.delete_document(db, document_id)


@router.get("/credentials", response_model=list[schemas.SharedCredentialResponse])
async def get_credentials(
    group_id: int = Depends(get_current_group_id),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List shared credentials for the current group."""
    await require_member(db, group_id, user.id)
    creds = await service.list_credentials(db, group_id)
    return [schemas.SharedCredentialResponse.model_validate(c) for c in creds]


@router.post(
    "/credentials",
    response_model=schemas.SharedCredentialResponse,
    status_code=status.HTTP_201_CREATED,
)
async def post_credentials(
    data: schemas.SharedCredentialCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new shared credential."""
    await require_member(db, data.group_id, user.id)
    cred = await service.create_credential(
        db,
        group_id=data.group_id,
        name=data.name,
        credential_type=data.credential_type,
        password=data.password,
        access_level=data.access_level,
        username_identity=data.username_identity,
        url=data.url,
        rotation_reminder_days=data.rotation_reminder_days,
        notes=data.notes,
    )
    return schemas.SharedCredentialResponse.model_validate(cred)


@router.get(
    "/credentials/{credential_id}/reveal",
    response_model=schemas.SharedCredentialWithPasswordResponse,
)
async def get_credentials_reveal(
    credential_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_introspection_user),
):
    """Reveal a credential's password. Requires re-authentication."""
    cred = await service.get_credential_by_id(db, credential_id)
    if not cred:
        raise NotFoundError(
            code="CREDENTIAL_NOT_FOUND", detail=f"Credential {credential_id} not found"
        )

    # Get user's role in the group
    from mitlist.modules.auth.interface import require_member

    membership = await require_member(db, cred.group_id, user.id)

    cred, decrypted = await service.reveal_credential(
        db,
        credential_id=credential_id,
        user_id=user.id,
        user_role=membership.role,
    )

    response_data = schemas.SharedCredentialResponse.model_validate(cred).model_dump()
    response_data["decrypted_password"] = decrypted
    return schemas.SharedCredentialWithPasswordResponse(**response_data)
