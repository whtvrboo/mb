import type {
  ListResponse,
  ListCreate,
  ListUpdate,
  ItemResponse,
  ItemCreate,
  ItemUpdate,
  ItemBulkCreate,
  ItemBulkResponse,
  InventoryItemResponse,
  InventoryItemUpdate,
} from '~/types/lists'

export function useLists() {
  const $api = useNuxtApp().$api

  return {
    listLists: (params?: {
      is_archived?: boolean
      list_type?: string
    }) => $api<ListResponse[]>('/lists', { query: params }),
    getList: (listId: number) =>
      useApi<ListResponse>(`/lists/${listId}`),
    createList: (data: ListCreate) =>
      $api<ListResponse>('/lists', { method: 'POST', body: data }),
    updateList: (listId: number, data: ListUpdate) =>
      $api<ListResponse>(`/lists/${listId}`, {
        method: 'PATCH',
        body: data,
      }),

    listItems: (listId: number) =>
      $api<ItemResponse[]>(`/lists/${listId}/items`),
    addItem: (listId: number, data: ItemCreate) =>
      $api<ItemResponse>(`/lists/${listId}/items`, {
        method: 'POST',
        body: data,
      }),
    updateItem: (listId: number, itemId: number, data: ItemUpdate) =>
      $api<ItemResponse>(`/lists/${listId}/items/${itemId}`, {
        method: 'PATCH',
        body: data,
      }),
    deleteItem: (listId: number, itemId: number) =>
      $api<void>(`/lists/${listId}/items/${itemId}`, {
        method: 'DELETE',
      }),
    bulkAddItems: (listId: number, data: ItemBulkCreate) =>
      $api<ItemBulkResponse>(`/lists/${listId}/items/bulk`, {
        method: 'POST',
        body: data,
      }),

    listInventory: () => useApi<InventoryItemResponse[]>('/inventory'),
    updateInventoryItem: (
      inventoryId: number,
      data: InventoryItemUpdate,
    ) =>
      $api<InventoryItemResponse>(`/inventory/${inventoryId}`, {
        method: 'PATCH',
        body: data,
      }),
  }
}
