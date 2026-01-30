import type {
  DocumentResponse,
  DocumentUploadRequest,
  DocumentUploadResponse,
  DocumentDownloadResponse,
  SharedCredentialResponse,
  SharedCredentialWithPasswordResponse,
  SharedCredentialCreate,
} from '~/types/documents'

export function useDocuments() {
  const $api = useNuxtApp().$api

  return {
    listDocuments: () => useApi<DocumentResponse[]>('/documents'),
    getUploadUrl: (data: DocumentUploadRequest) =>
      $api<DocumentUploadResponse>('/documents/upload', {
        method: 'POST',
        body: data,
      }),
    getDownloadUrl: (documentId: number) =>
      useApi<DocumentDownloadResponse>(`/documents/${documentId}/download`),
    deleteDocument: (documentId: number) =>
      $api<void>(`/documents/${documentId}`, { method: 'DELETE' }),

    listCredentials: () =>
      useApi<SharedCredentialResponse[]>('/credentials'),
    createCredential: (data: SharedCredentialCreate) =>
      $api<SharedCredentialResponse>('/credentials', {
        method: 'POST',
        body: data,
      }),
    revealCredential: (credentialId: number) =>
      useApi<SharedCredentialWithPasswordResponse>(
        `/credentials/${credentialId}/reveal`,
      ),
  }
}
