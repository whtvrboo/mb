"""
Governance module PUBLIC interface.

Other modules may ONLY import from this file (and schemas.py).
Never import models or service directly from other modules.
"""

from mitlist.modules.governance import schemas, service

__all__ = [
    "schemas",
    # Proposals
    "list_proposals",
    "get_proposal_by_id",
    "create_proposal",
    "update_proposal",
    "open_proposal",
    "cancel_proposal",
    # Voting
    "get_user_vote",
    "cast_vote",
    "cast_ranked_votes",
    # Closing/Execution
    "close_proposal",
    "execute_proposal",
]

list_proposals = service.list_proposals
get_proposal_by_id = service.get_proposal_by_id
create_proposal = service.create_proposal
update_proposal = service.update_proposal
open_proposal = service.open_proposal
cancel_proposal = service.cancel_proposal

get_user_vote = service.get_user_vote
cast_vote = service.cast_vote
cast_ranked_votes = service.cast_ranked_votes

close_proposal = service.close_proposal
execute_proposal = service.execute_proposal
