import type {
  HomeAssetResponse,
  HomeAssetCreate,
  HomeAssetUpdate,
  HomeAssetDisposeRequest,
  MaintenanceTaskResponse,
  MaintenanceTaskCreate,
  MaintenanceTaskUpdate,
  MaintenanceLogResponse,
  MaintenanceCompleteRequest,
  AssetInsuranceResponse,
  AssetInsuranceCreate,
  AssetInsuranceUpdate,
} from '~/types/assets'

export function useAssets() {
  const $api = useNuxtApp().$api

  return {
    listAssets: () => useApi<HomeAssetResponse[]>('/assets'),
    getAsset: (assetId: number) =>
      useApi<HomeAssetResponse>(`/assets/${assetId}`),
    createAsset: (data: HomeAssetCreate) =>
      $api<HomeAssetResponse>('/assets', { method: 'POST', body: data }),
    updateAsset: (assetId: number, data: HomeAssetUpdate) =>
      $api<HomeAssetResponse>(`/assets/${assetId}`, {
        method: 'PATCH',
        body: data,
      }),
    disposeAsset: (assetId: number, data: HomeAssetDisposeRequest) =>
      $api<HomeAssetResponse>(`/assets/${assetId}/dispose`, {
        method: 'POST',
        body: data,
      }),

    listMaintenanceTasks: (assetId: number) =>
      useApi<MaintenanceTaskResponse[]>(`/assets/${assetId}/tasks`),
    createMaintenanceTask: (assetId: number, data: MaintenanceTaskCreate) =>
      $api<MaintenanceTaskResponse>(`/assets/${assetId}/tasks`, {
        method: 'POST',
        body: data,
      }),
    updateMaintenanceTask: (
      taskId: number,
      data: MaintenanceTaskUpdate,
    ) =>
      $api<MaintenanceTaskResponse>(`/assets/tasks/${taskId}`, {
        method: 'PATCH',
        body: data,
      }),

    listMaintenanceLogs: (taskId: number) =>
      useApi<MaintenanceLogResponse[]>(`/assets/tasks/${taskId}/logs`),
    createMaintenanceLog: (
      taskId: number,
      data: MaintenanceCompleteRequest,
    ) =>
      $api<MaintenanceLogResponse>(`/assets/tasks/${taskId}/logs`, {
        method: 'POST',
        body: data,
      }),

    listInsurances: () => useApi<AssetInsuranceResponse[]>('/assets/insurance'),
    createInsurance: (data: AssetInsuranceCreate) =>
      $api<AssetInsuranceResponse>('/assets/insurance', {
        method: 'POST',
        body: data,
      }),
    updateInsurance: (
      insuranceId: number,
      data: AssetInsuranceUpdate,
    ) =>
      $api<AssetInsuranceResponse>(`/assets/insurance/${insuranceId}`, {
        method: 'PATCH',
        body: data,
      }),
  }
}
