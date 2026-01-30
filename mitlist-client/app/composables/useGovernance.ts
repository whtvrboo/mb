import type {
  ProposalResponse,
  ProposalCreate,
  ProposalUpdate,
  BallotOptionResponse,
  VoteResponse,
  VoteCreate,
  RankedVoteCreate,
  ProposalResultResponse,
} from '~/types/governance'

export function useGovernance() {
  const $api = useNuxtApp().$api

  return {
    listProposals: (params?: {
      status_filter?: string
      limit?: number
      offset?: number
    }) => useApi<ProposalResponse[]>('/proposals', { query: params }),
    getProposal: (proposalId: number) =>
      useApi<ProposalResponse>(`/proposals/${proposalId}`),
    createProposal: (data: ProposalCreate) =>
      $api<ProposalResponse>('/proposals', { method: 'POST', body: data }),
    updateProposal: (proposalId: number, data: ProposalUpdate) =>
      $api<ProposalResponse>(`/proposals/${proposalId}`, {
        method: 'PATCH',
        body: data,
      }),
    cancelProposal: (proposalId: number) =>
      $api<ProposalResponse>(`/proposals/${proposalId}`, {
        method: 'DELETE',
      }),

    openProposal: (proposalId: number) =>
      $api<ProposalResponse>(`/proposals/${proposalId}/open`, {
        method: 'POST',
      }),
    closeProposal: (proposalId: number) =>
      $api<ProposalResponse>(`/proposals/${proposalId}/close`, {
        method: 'POST',
      }),
    executeProposal: (proposalId: number) =>
      $api<ProposalResponse>(`/proposals/${proposalId}/execute`, {
        method: 'POST',
      }),

    getProposalOptions: (proposalId: number) =>
      useApi<BallotOptionResponse[]>(`/proposals/${proposalId}/options`),

    castVote: (proposalId: number, data: VoteCreate) =>
      $api<VoteResponse>(`/proposals/${proposalId}/vote`, {
        method: 'POST',
        body: data,
      }),
    castRankedVote: (proposalId: number, data: RankedVoteCreate) =>
      $api<VoteResponse[]>(`/proposals/${proposalId}/vote/ranked`, {
        method: 'POST',
        body: data,
      }),
    getMyVote: (proposalId: number) =>
      useApi<VoteResponse | null>(`/proposals/${proposalId}/vote/me`),

    getProposalResults: (proposalId: number) =>
      useApi<ProposalResultResponse>(`/proposals/${proposalId}/results`),
  }
}
