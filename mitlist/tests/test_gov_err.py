import asyncio
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient

from mitlist.modules.governance.schemas import ProposalCreate

def run():
    deadline = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat() + "Z"
    create_data = {
        "group_id": 1,
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
    try:
        ProposalCreate(**create_data)
        print("Success")
    except Exception as e:
        print("Error:", repr(e))

if __name__ == "__main__":
    run()
