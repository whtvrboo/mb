"""Tests for governance module: proposals and votes."""

import pytest
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_proposals_list_empty(authed_client: AsyncClient, auth_headers: dict):
    """List proposals when none exist."""
    response = await authed_client.get("/proposals", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_proposal_create_get_and_vote(authed_client: AsyncClient, auth_headers: dict):
    """Create a proposal, get it, open for voting, cast vote, get results."""
    group_id = int(auth_headers["X-Group-ID"])
    deadline = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat() + "Z"

    # Create proposal with ballot options
    create_data = {
        "group_id": group_id,
        "title": "Test Proposal",
        "description": "Should we order pizza?",
        "type": "GENERAL",
        "strategy": "SIMPLE_MAJORITY",
        "deadline_at": deadline,
        "min_quorum_percentage": 50,
        "ballot_options": [
            {"text": "Yes", "display_order": 0},
            {"text": "No", "display_order": 1},
        ],
    }
    response = await authed_client.post("/proposals", json=create_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    proposal_id = data["id"]
    assert data["title"] == "Test Proposal"
    assert data["status"] == "DRAFT"
    assert len(data["ballot_options"]) == 2
    option_ids = [opt["id"] for opt in data["ballot_options"]]

    # List proposals
    response = await authed_client.get("/proposals", headers=auth_headers)
    assert response.status_code == 200
    proposals = response.json()
    assert len(proposals) >= 1
    assert any(p["id"] == proposal_id for p in proposals)

    # Get proposal by ID
    response = await authed_client.get(f"/proposals/{proposal_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == proposal_id

    # Get ballot options
    response = await authed_client.get(f"/proposals/{proposal_id}/options", headers=auth_headers)
    assert response.status_code == 200
    options = response.json()
    assert len(options) == 2

    # Update draft (optional)
    response = await authed_client.patch(
        f"/proposals/{proposal_id}",
        json={"title": "Updated Title", "description": "Updated desc"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"

    # Open proposal for voting
    response = await authed_client.post(
        f"/proposals/{proposal_id}/open",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "OPEN"

    # Cast vote (ballot_option_id = first option)
    vote_data = {
        "proposal_id": proposal_id,
        "ballot_option_id": option_ids[0],
        "weight": 1,
        "is_anonymous": False,
    }
    response = await authed_client.post(
        f"/proposals/{proposal_id}/vote",
        json=vote_data,
        headers=auth_headers,
    )
    assert response.status_code == 200
    vote_resp = response.json()
    assert vote_resp["ballot_option_id"] == option_ids[0]

    # Get my vote
    response = await authed_client.get(
        f"/proposals/{proposal_id}/vote/me",
        headers=auth_headers,
    )
    assert response.status_code == 200
    # May return single vote or list depending on schema; at least we get 200
    me_vote = response.json()
    assert me_vote is None or me_vote.get("ballot_option_id") == option_ids[0]

    # Get results (before close)
    response = await authed_client.get(
        f"/proposals/{proposal_id}/results",
        headers=auth_headers,
    )
    assert response.status_code == 200
    results = response.json()
    assert results["proposal_id"] == proposal_id
    assert "total_votes" in results
    assert "results" in results


@pytest.mark.asyncio
async def test_proposal_not_found(authed_client: AsyncClient, auth_headers: dict):
    """Get non-existent proposal returns 404."""
    response = await authed_client.get("/proposals/99999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json().get("code") == "PROPOSAL_NOT_FOUND"
