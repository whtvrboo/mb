import type {
  PlantSpeciesResponse,
  PlantResponse,
  PlantWithSpeciesResponse,
  PlantCreate,
  PlantUpdate,
  PlantMarkDeadRequest,
  PlantLogResponse,
  PlantLogCreate,
  PlantScheduleResponse,
  PlantScheduleCreate,
  PlantScheduleMarkDoneRequest,
} from '~/types/plants'

export function usePlants() {
  const $api = useNuxtApp().$api

  return {
    listSpecies: () => useApi<PlantSpeciesResponse[]>('/plants/species'),

    listPlants: () => useApi<PlantResponse[]>('/plants'),
    getPlant: (plantId: number) =>
      useApi<PlantWithSpeciesResponse>(`/plants/${plantId}`),
    createPlant: (data: PlantCreate) =>
      $api<PlantResponse>('/plants', { method: 'POST', body: data }),
    updatePlant: (plantId: number, data: PlantUpdate) =>
      $api<PlantResponse>(`/plants/${plantId}`, {
        method: 'PATCH',
        body: data,
      }),
    markDead: (plantId: number, data: PlantMarkDeadRequest) =>
      $api<PlantResponse>(`/plants/${plantId}/mark-dead`, {
        method: 'POST',
        body: data,
      }),

    listLogs: (plantId: number) =>
      useApi<PlantLogResponse[]>(`/plants/${plantId}/logs`),
    createLog: (plantId: number, data: PlantLogCreate) =>
      $api<PlantLogResponse>(`/plants/${plantId}/logs`, {
        method: 'POST',
        body: data,
      }),

    listSchedules: (plantId: number) =>
      useApi<PlantScheduleResponse[]>(`/plants/${plantId}/schedules`),
    createSchedule: (plantId: number, data: PlantScheduleCreate) =>
      $api<PlantScheduleResponse>(`/plants/${plantId}/schedules`, {
        method: 'POST',
        body: data,
      }),
    markScheduleDone: (
      scheduleId: number,
      data: PlantScheduleMarkDoneRequest,
    ) =>
      $api<PlantScheduleResponse>(`/plants/schedules/${scheduleId}/done`, {
        method: 'PATCH',
        body: data,
      }),
  }
}
