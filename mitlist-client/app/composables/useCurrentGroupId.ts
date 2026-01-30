/**
 * Current group context (for API requests that require X-Group-Id or group_id query).
 * Set this when the user selects a group; the API plugin will send it as X-Group-Id header.
 */
export function useCurrentGroupId() {
  return useState<number | null>('current-group-id', () => null)
}
