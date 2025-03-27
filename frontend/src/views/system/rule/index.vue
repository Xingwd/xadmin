<template>
    <div class="default-main xa-table-box">
        <el-alert class="xa-table-alert" v-if="xaTable.table.remark" :title="xaTable.table.remark" type="info" show-icon />

        <!-- 表格顶部菜单 -->
        <TableHeader
            :buttons="['refresh', 'add', 'edit', 'delete', 'unfold', 'quickSearch', 'columnDisplay']"
            :quick-search-placeholder="t('Quick search placeholder', { fields: t('Title') })"
        />
        <!-- 表格 -->
        <!-- 要使用`el-table`组件原有的属性，直接加在Table标签上即可 -->
        <Table ref="tableRef" :pagination="false" />

        <!-- 表单 -->
        <PopupForm />
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, provide } from 'vue'
import PopupForm from './popupForm.vue'
import Table from '/@/components/table/index.vue'
import TableHeader from '/@/components/table/header/index.vue'
import { defaultOptButtons } from '/@/components/table'
import { useI18n } from 'vue-i18n'
import XaTableClass from '/@/utils/xaTable'
import { rulesReadRules, rulesCreateRule, rulesUpdateRule, rulesDeleteRule } from '/@/client'

defineOptions({
    name: 'system/rule',
})

const { t } = useI18n()
const tableRef = ref()
const xaTable = new XaTableClass(
    {
        queryKey: 'rules',
        index: rulesReadRules,
        add: rulesCreateRule,
        edit: rulesUpdateRule,
        del: rulesDeleteRule,
    },
    {
        expandAll: false,
        dblClickNotEditColumn: [undefined, 'cache', 'status'],
        column: [
            { type: 'selection', align: 'center' },
            { label: t('Title'), prop: 'title', align: 'left', width: '200' },
            { label: t('utils.Icon'), prop: 'icon', align: 'center', width: '60', render: 'icon', default: 'fa fa-circle-o' },
            { label: t('Name'), prop: 'name', align: 'center', showOverflowTooltip: true },
            {
                label: t('utils.type'),
                prop: 'type',
                align: 'center',
                render: 'tag',
                custom: { menu_item: 'danger', menu_dir: 'success', button: 'info' },
                replaceValue: {
                    menu_item: t('system.rules.type menu_item'),
                    menu_dir: t('system.rules.type menu_dir'),
                    permission: t('system.rules.type permission'),
                },
            },
            { label: t('Weight'), prop: 'weight', align: 'center', width: '100' },
            { label: t('Cache'), prop: 'cache', align: 'center', width: '80', render: 'switch' },
            {
                label: t('State'),
                prop: 'status',
                align: 'center',
                width: '80',
                render: 'tag',
                custom: { false: 'warning', true: 'primary' },
                replaceValue: { false: t('Disable'), true: t('Enable') },
            },
            { label: t('Update time'), prop: 'updated_at', align: 'center', width: '160', render: 'datetime' },
            { label: t('Create time'), prop: 'created_at', align: 'center', width: '160', render: 'datetime' },
            {
                label: t('Operate'),
                align: 'center',
                width: '130',
                render: 'buttons',
                buttons: defaultOptButtons(['edit', 'delete']),
            },
        ],
    },
    {
        defaultItems: {
            type: 'menu_item',
            menu_item_type: 'tab',
            cache: false,
            status: true,
            icon: 'fa fa-circle-o',
        },
    },
    {
        index: () => {
            xaTable.table.expandAll = xaTable.table.query?.quick_search ? true : false
        },
        onTableDblclick: (): boolean => {
            return xaTable.auth('edit')
        },
    }
)

provide('xaTable', xaTable)

xaTable.mount()

onMounted(() => {
    xaTable.table.ref = tableRef.value
})
</script>

<style scoped lang="scss"></style>
