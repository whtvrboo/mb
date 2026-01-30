/** Documents module types: Document, SharedCredential */

export interface DocumentResponse {
  id: number
  group_id: number
  uploaded_by_id: number
  file_name: string
  mime_type: string
  folder_path: string | null
  file_key: string
  file_size_bytes: number
  tags: string[] | null
  is_encrypted: boolean
  created_at: string
  updated_at: string
}

export interface DocumentUploadRequest {
  group_id: number
  file_name: string
  mime_type: string
  file_size_bytes: number
  folder_path?: string | null
}

export interface DocumentUploadResponse {
  upload_url: string
  file_key: string
  expires_in_seconds: number
}

export interface DocumentDownloadResponse {
  download_url: string
  expires_in_seconds: number
}

export interface SharedCredentialResponse {
  id: number
  group_id: number
  name: string
  credential_type: string
  username_identity: string | null
  access_level: string
  url: string | null
  rotation_reminder_days: number | null
  notes: string | null
  last_rotated_at: string | null
  created_at: string
  updated_at: string
}

export interface SharedCredentialWithPasswordResponse extends SharedCredentialResponse {
  decrypted_password: string
}

export interface SharedCredentialCreate {
  group_id: number
  name: string
  credential_type: string
  username_identity?: string | null
  password: string
  access_level: string
  url?: string | null
  rotation_reminder_days?: number | null
  notes?: string | null
}
