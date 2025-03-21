<template>
    <div>
        <el-switch v-if="field.prop" @change="onChange" :model-value="cellValue" :loading="isLoading" />
    </div>
</template>

<script setup lang="ts">
import { TableColumnCtx } from 'element-plus'
import { cloneDeep } from 'lodash-es'
import { inject, ref } from 'vue'
import { getCellValue } from '/@/components/table/index'
import type XaTableClass from '/@/utils/xaTable'
import { useMutation } from '@pinia/colada'

interface Props {
    row: TableRow
    field: TableColumn
    column: TableColumnCtx<TableRow>
    index: number
}

const props = defineProps<Props>()
const xaTable = inject('xaTable') as XaTableClass
const cellValue = ref(getCellValue(props.row, props.field, props.column, props.index))
const { mutate, isLoading } = useMutation({
    mutation: (vars: anyObj) => xaTable.api.edit!({ path: { [xaTable.table.pk!]: vars.id }, body: vars.body }),
    onSuccess: (_data, vars, _context) => {
        cellValue.value = vars.value
        xaTable.onTableAction('field-change', { value: vars.value, ...props })
    },
    onError: (error) => {
        console.error(error)
    },
    onSettled: () => {
        // invalidate the query to refetch the new data
        xaTable.queryCache.invalidateQueries({ key: xaTable.queryKey.value })
    },
})

if (typeof cellValue.value === 'number') {
    cellValue.value = cellValue.value.toString()
}

const onChange = (value: string | number | boolean) => {
    const data = Object.assign(cloneDeep(props.row), { [props.field.prop!]: value })
    mutate({ id: data.id, body: data, value: value })
}
</script>
