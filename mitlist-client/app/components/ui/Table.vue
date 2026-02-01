<script setup lang="ts">
interface Column {
    key: string
    label: string
    class?: string
}

interface Props {
    columns: Column[]
    rows: any[]
    rowKey?: string | ((row: any) => string | number)
}

const props = defineProps<Props>()

const getRowKey = (row: any, index: number) => {
    if (typeof props.rowKey === 'function') {
        return props.rowKey(row)
    }
    if (typeof props.rowKey === 'string') {
        const key = row[props.rowKey]
        if (key !== undefined && key !== null) return key
    }
    return index
}
</script>

<template>
    <div class="w-full overflow-x-auto rounded-xl border-[3px] border-background-dark shadow-[6px_6px_0px_0px_#221f10]">
        <table class="w-full bg-white text-left border-collapse">
            <thead>
                <tr class="bg-gray-100 border-b-[3px] border-background-dark">
                    <th v-for="col in columns" :key="col.key"
                        class="px-6 py-4 font-bold uppercase text-sm tracking-wider text-gray-600" :class="col.class">
                        {{ col.label }}
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(row, rowIndex) in rows" :key="getRowKey(row, rowIndex)"
                    class="border-b-[2px] border-background-dark last:border-b-0 hover:bg-yellow-50/50 transition-colors group">
                    <td v-for="col in columns" :key="col.key"
                        class="px-6 py-4 font-medium text-background-dark" :class="col.class">
                        <slot :name="col.key" :row="row" :index="rowIndex">
                            {{ row[col.key] }}
                        </slot>
                    </td>
                </tr>
                <tr v-if="rows.length === 0">
                    <td :colspan="columns.length" class="px-6 py-8 text-center text-gray-500 font-bold">
                        No data available
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>
