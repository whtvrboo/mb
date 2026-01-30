import type {
  PetResponse,
  PetCreate,
  PetUpdate,
  PetMarkDeceasedRequest,
  PetMedicalRecordResponse,
  PetMedicalRecordCreate,
  PetLogResponse,
  PetLogCreate,
  PetScheduleResponse,
  PetScheduleCreate,
  PetScheduleMarkDoneRequest,
} from '~/types/pets'

export function usePets() {
  const $api = useNuxtApp().$api

  return {
    listPets: () => useApi<PetResponse[]>('/pets'),
    getPet: (petId: number) => useApi<PetResponse>(`/pets/${petId}`),
    createPet: (data: PetCreate) =>
      $api<PetResponse>('/pets', { method: 'POST', body: data }),
    updatePet: (petId: number, data: PetUpdate) =>
      $api<PetResponse>(`/pets/${petId}`, {
        method: 'PATCH',
        body: data,
      }),
    markDeceased: (petId: number, data: PetMarkDeceasedRequest) =>
      $api<PetResponse>(`/pets/${petId}/mark-deceased`, {
        method: 'POST',
        body: data,
      }),

    getExpiringVaccines: (params?: { days_ahead?: number }) =>
      useApi<PetMedicalRecordResponse[]>('/pets/vaccines/expiring', {
        query: params,
      }),

    listMedicalRecords: (petId: number) =>
      useApi<PetMedicalRecordResponse[]>(`/pets/${petId}/medical`),
    createMedicalRecord: (petId: number, data: PetMedicalRecordCreate) =>
      $api<PetMedicalRecordResponse>(`/pets/${petId}/medical`, {
        method: 'POST',
        body: data,
      }),

    listLogs: (petId: number) =>
      useApi<PetLogResponse[]>(`/pets/${petId}/logs`),
    createLog: (petId: number, data: PetLogCreate) =>
      $api<PetLogResponse>(`/pets/${petId}/logs`, {
        method: 'POST',
        body: data,
      }),

    listSchedules: (petId: number) =>
      useApi<PetScheduleResponse[]>(`/pets/${petId}/schedules`),
    createSchedule: (petId: number, data: PetScheduleCreate) =>
      $api<PetScheduleResponse>(`/pets/${petId}/schedules`, {
        method: 'POST',
        body: data,
      }),
    markScheduleDone: (
      scheduleId: number,
      data: PetScheduleMarkDoneRequest,
    ) =>
      $api<PetScheduleResponse>(`/pets/schedules/${scheduleId}/done`, {
        method: 'PATCH',
        body: data,
      }),
  }
}
