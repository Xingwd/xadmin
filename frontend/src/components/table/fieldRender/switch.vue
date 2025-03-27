<template>
    <div>
        <el-switch v-if="field.prop" :disabled="!xaTable.auth('edit')" :model-value="cellValue" :loading="isLoading" @change="onChange" />
    </div>
</template>

<script setup lang="ts">
import { TableColumnCtx } from 'element-plus'
import { cloneDeep } from 'lodash-es'
import { inject, ref } from 'vue'
import { useMutation } from '@pinia/colada'
import { getCellValue } from '/@/components/table/index'
import type XaTableClass from '/@/utils/xaTable'
import { httpStatusHandle, isSuccess } from '/@/utils/request'

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
    onSuccess: (data, vars, _context) => {
        httpStatusHandle(data)
        const status = (data as anyObj).status
        if (status && typeof status === 'number' && isSuccess(status)) {
            cellValue.value = vars.value
            xaTable.onTableAction('field-change', { value: vars.value, ...props })
        }
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
