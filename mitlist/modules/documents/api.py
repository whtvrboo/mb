"""Documents & Files module FastAPI router. Handles /documents and /credentials."""

from typing import List as ListType

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api.deps import get_db
from mitlist.core.errors import NotImplementedAppError
from mitlist.modules.documents import schemas

router = APIRouter(tags=["documents", "credentials"])


def _stub(msg: str):
    raise NotImplementedAppError(detail=msg)


@router.get("/documents", response_model=ListType[schemas.DocumentResponse])
async def get_documents(group_id: int, db: AsyncSession = Depends(get_db)):
    _stub("GET /documents is not yet implemented")


@router.post("/documents/upload", response_model=schemas.DocumentUploadResponse)
async def post_documents_upload(data: schemas.DocumentUploadRequest, db: AsyncSession = Depends(get_db)):
    _stub("POST /documents/upload is not yet implemented")


@router.get("/documents/{document_id}/download", response_model=schemas.DocumentDownloadResponse)
async def get_documents_download(document_id: int, db: AsyncSession = Depends(get_db)):
    _stub("GET /documents/{id}/download is not yet implemented")


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: int, db: AsyncSession = Depends(get_db)):
    _stub("DELETE /documents/{id} is not yet implemented")


@router.get("/credentials", response_model=ListType[schemas.SharedCredentialResponse])
async def get_credentials(group_id: int, db: AsyncSession = Depends(get_db)):
    _stub("GET /credentials is not yet implemented")


@router.post("/credentials", response_model=schemas.SharedCredentialResponse, status_code=status.HTTP_201_CREATED)
async def post_credentials(data: schemas.SharedCredentialCreate, db: AsyncSession = Depends(get_db)):
    _stub("POST /credentials is not yet implemented")


@router.get("/credentials/{credential_id}/reveal", response_model=schemas.SharedCredentialWithPasswordResponse)
async def get_credentials_reveal(credential_id: int, db: AsyncSession = Depends(get_db)):
    _stub("GET /credentials/{id}/reveal is not yet implemented")
