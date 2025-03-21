<template>
    <div class="default-main xa-table-box">
        <el-alert class="xa-table-alert" v-if="xaTable.table.remark" :title="xaTable.table.remark" type="info" show-icon />

        <!-- 表格顶部菜单 -->
        <TableHeader
            :buttons="['refresh', 'delete', 'commonSearch', 'quickSearch', 'columnDisplay']"
            :quick-search-placeholder="t('Quick search placeholder', { fields: t('Title') })"
        />
        <!-- 表格 -->
        <!-- 要使用`el-table`组件原有的属性，直接加在Table标签上即可 -->
        <Table />

        <Info />
    </div>
</template>

<script setup lang="ts">
import { concat, cloneDeep } from 'lodash-es'
import { provide } from 'vue'
import XaTableClass from '/@/utils/xaTable'
import Table from '/@/components/table/index.vue'
import TableHeader from '/@/components/table/header/index.vue'
import { defaultOptButtons } from '/@/components/table'
import { useI18n } from 'vue-i18n'
import Info from './info.vue'
import { buildJsonToElTreeData } from '/@/utils/common'
import { operationLogsReadOperationLogs, operationLogsDeleteOperationLog } from '/@/client'

defineOptions({
    name: 'system/operationLog',
})

const { t } = useI18n()

let optButtons: OptButton[] = [
    {
        render: 'tipButton',
        name: 'info',
        title: 'Info',
        text: '',
        type: 'primary',
        icon: 'fa fa-search-plus',
        class: 'table-row-edit',
        disabledTip: false,
        click: (row: TableRow) => {
            infoButtonClick(row)
        },
    },
]

optButtons = concat(optButtons, defaultOptButtons(['delete']))

const xaTable = new XaTableClass(
    {
        queryKey: 'operation-logs',
        index: operationLogsReadOperationLogs,
        del: operationLogsDeleteOperationLog,
    },
    {
        column: [
            { type: 'selection', align: 'center', operator: false },
            { type: 'index', align: 'center', operator: false },
            {
                label: t('system.operationLogs.username'),
                prop: 'username',
                align: 'center',
                operator: 'LIKE',
                operatorPlaceholder: t('Fuzzy query'),
                width: 160,
            },
            {
                label: t('Title'),
                prop: 'title',
                align: 'center',
                operator: 'LIKE',
                operatorPlaceholder: t('Fuzzy query'),
            },
            {
                label: t('system.operationLogs.Request Method'),
                prop: 'request_method',
                align: 'center',
                width: '100',
                operator: 'eq',
                render: 'tag',
                custom: { GET: 'primary', POST: 'success', PUT: 'warning', DELETE: 'danger' },
                replaceValue: { GET: 'GET', POST: 'POST', PUT: 'PUT', DELETE: 'DELETE' },
            },
            {
                label: t('system.operationLogs.Request Path'),
                prop: 'request_path',
                align: 'center',
                operator: 'LIKE',
                operatorPlaceholder: t('Fuzzy query'),
                showOverflowTooltip: true,
            },
            {
                label: t('system.operationLogs.Request Query Params'),
                prop: 'request_query_params',
                align: 'center',
                operator: 'LIKE',
                operatorPlaceholder: t('Fuzzy query'),
                showOverflowTooltip: true,
            },
            {
                label: t('system.operationLogs.Response Status Code'),
                prop: 'response_status_code',
                propType: 'number',
                align: 'center',
                width: '120',
                operator: 'eq',
            },
            {
                label: t('Create time'),
                prop: 'created_at',
                align: 'center',
                render: 'datetime',
                sortable: 'custom',
                operator: 'RANGE',
                width: 160,
            },
            {
                label: t('Operate'),
                align: 'center',
                width: '100',
                render: 'buttons',
                buttons: optButtons,
                operator: false,
            },
        ],
        dblClickNotEditColumn: [undefined],
    },
    {},
    {
        onTableDblclick: ({ row }) => {
            infoButtonClick(row)
            return false
        },
    }
)

/** 点击查看详情按钮响应 */
const infoButtonClick = (row: TableRow) => {
    if (!row) return
    // 数据来自表格数据,未重新请求api,深克隆,不然可能会影响表格
    let rowClone = cloneDeep(row)
    rowClone.data = rowClone.request_query_params
        ? [{ label: '点击展开', children: buildJsonToElTreeData(JSON.parse(rowClone.request_query_params)) }]
        : []
    xaTable.form.extend!.info = rowClone
    xaTable.form.operate = 'Info'
}

provide('xaTable', xaTable)

xaTable.mount()
</script>

<style scoped lang="scss"></style>
