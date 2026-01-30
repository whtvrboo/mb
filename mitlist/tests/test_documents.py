"""Tests for documents and credentials API."""

import pytest
from httpx import AsyncClient

from mitlist.modules.documents.service import create_document, get_document_by_id


@pytest.mark.asyncio
async def test_documents_list_empty(authed_client: AsyncClient, auth_headers: dict):
    """List documents when none exist returns empty list."""
    response = await authed_client.get("/documents", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_documents_upload_returns_url_and_creates_document(
    authed_client: AsyncClient, auth_headers: dict
):
    """POST /documents/upload returns presigned URL and creates document record."""
    group_id = int(auth_headers["X-Group-ID"])
    data = {
        "group_id": group_id,
        "file_name": "test.pdf",
        "mime_type": "application/pdf",
        "file_size_bytes": 1024,
        "folder_path": "/inbox",
    }
    response = await authed_client.post("/documents/upload", json=data, headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert "upload_url" in body
    assert "file_key" in body
    assert "expires_in_seconds" in body
    assert "groups/" in body["file_key"]
    assert "test.pdf" in body["file_key"] or "test" in body["file_key"]


@pytest.mark.asyncio
async def test_documents_list_after_upload(
    authed_client: AsyncClient, auth_headers: dict, db_session, test_user, test_group
):
    """List documents returns the created document after upload."""
    group_id = test_group.id
    await create_document(
        db_session,
        group_id=group_id,
        uploaded_by_id=test_user.id,
        file_name="manual.pdf",
        file_key="groups/1/documents/manual.pdf",
        mime_type="application/pdf",
        file_size_bytes=2048,
        folder_path="/manuals",
    )
    await db_session.commit()

    response = await authed_client.get("/documents", headers=auth_headers)
    assert response.status_code == 200
    docs = response.json()
    assert len(docs) >= 1
    doc = next((d for d in docs if d["file_name"] == "manual.pdf"), None)
    assert doc is not None
    assert doc["mime_type"] == "application/pdf"
    assert doc["file_size_bytes"] == 2048
    assert doc["folder_path"] == "/manuals"


@pytest.mark.asyncio
async def test_documents_download_url(
    authed_client: AsyncClient, auth_headers: dict, db_session, test_user, test_group
):
    """GET /documents/{id}/download returns presigned download URL."""
    group_id = test_group.id
    doc = await create_document(
        db_session,
        group_id=group_id,
        uploaded_by_id=test_user.id,
        file_name="readme.pdf",
        file_key="groups/1/documents/readme.pdf",
        mime_type="application/pdf",
        file_size_bytes=512,
    )
    await db_session.commit()

    response = await authed_client.get(
        f"/documents/{doc.id}/download", headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert "download_url" in body
    assert "expires_in_seconds" in body


@pytest.mark.asyncio
async def test_documents_delete(
    authed_client: AsyncClient, auth_headers: dict, db_session, test_user, test_group
):
    """DELETE /documents/{id} soft-deletes document."""
    group_id = test_group.id
    doc = await create_document(
        db_session,
        group_id=group_id,
        uploaded_by_id=test_user.id,
        file_name="to_delete.pdf",
        file_key="groups/1/documents/to_delete.pdf",
        mime_type="application/pdf",
        file_size_bytes=100,
    )
    await db_session.commit()
    doc_id = doc.id

    response = await authed_client.delete(
        f"/documents/{doc_id}", headers=auth_headers
    )
    assert response.status_code == 204

    # Document should be soft-deleted (get_document_by_id excludes deleted)
    doc_after = await get_document_by_id(db_session, doc_id)
    assert doc_after is None


@pytest.mark.asyncio
async def test_credentials_list_empty(authed_client: AsyncClient, auth_headers: dict):
    """List credentials when none exist returns empty list."""
    response = await authed_client.get("/credentials", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_credentials_create_and_list(authed_client: AsyncClient, auth_headers: dict):
    """Create credential and list returns it (without password)."""
    group_id = int(auth_headers["X-Group-ID"])
    data = {
        "group_id": group_id,
        "name": "WiFi Home",
        "credential_type": "WIFI",
        "password": "secret123",
        "access_level": "MEMBER",
        "username_identity": "admin",
        "url": "http://router.local",
        "notes": "Main router",
    }
    response = await authed_client.post("/credentials", json=data, headers=auth_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "WiFi Home"
    assert body["credential_type"] == "WIFI"
    assert "password" not in body
    assert "decrypted_password" not in body
    cred_id = body["id"]

    response = await authed_client.get("/credentials", headers=auth_headers)
    assert response.status_code == 200
    creds = response.json()
    assert len(creds) >= 1
    c = next((x for x in creds if x["id"] == cred_id), None)
    assert c is not None
    assert c["name"] == "WiFi Home"
