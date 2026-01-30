/** Governance module types: Proposal, BallotOption, Vote */

export interface BallotOptionResponse {
  id: number
  proposal_id: number
  text: string
  display_order: number
  option_metadata: Record<string, unknown> | null
  vote_count?: number
  created_at: string
  updated_at: string
}

export interface ProposalResponse {
  id: number
  group_id: number
  created_by_id: number
  title: string
  description: string | null
  type: string
  strategy: string
  deadline_at: string | null
  min_quorum_percentage: number | null
  status: string
  linked_expense_id: number | null
  linked_chore_id: number | null
  linked_pet_id: number | null
  execution_result: Record<string, unknown> | null
  executed_at: string | null
  created_at: string
  updated_at: string
  ballot_options: BallotOptionResponse[]
}

export interface ProposalCreate {
  title: string
  description?: string | null
  type: string
  strategy: string
  deadline_at?: string | null
  min_quorum_percentage?: number | null
  ballot_options: { text: string; display_order?: number; option_metadata?: Record<string, unknown> | null }[]
  linked_expense_id?: number | null
  linked_chore_id?: number | null
  linked_pet_id?: number | null
}

export interface ProposalUpdate {
  title?: string | null
  description?: string | null
  deadline_at?: string | null
  min_quorum_percentage?: number | null
}

export interface VoteResponse {
  id: number
  proposal_id: number
  user_id: number
  ballot_option_id: number
  rank_order: number | null
  weight: number
  is_anonymous: boolean
  voted_at: string
  created_at: string
  updated_at: string
}

export interface VoteCreate {
  ballot_option_id: number
  weight?: number
  is_anonymous?: boolean
}

export interface RankedVoteChoice {
  ballot_option_id: number
  rank: number
}

export interface RankedVoteCreate {
  ranked_choices: RankedVoteChoice[]
  is_anonymous?: boolean
}

export interface ProposalResultResponse {
  proposal_id: number
  status: string
  total_votes: number
  quorum_reached: boolean
  required_quorum: number | null
  results: { option_id: number; option_text: string; vote_count: number; percentage: number }[]
  winner_option_id: number | null
  winner_option_text: string | null
}
