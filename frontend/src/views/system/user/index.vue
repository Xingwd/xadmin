<template>
    <div class="default-main xa-table-box">
        <el-alert class="xa-table-alert" v-if="xaTable.table.remark" :title="xaTable.table.remark" type="info" show-icon />

        <!-- 表格顶部菜单 -->
        <TableHeader
            :buttons="['refresh', 'add', 'edit', 'delete', 'quickSearch', 'columnDisplay', 'commonSearch']"
            :quick-search-placeholder="t('Quick search placeholder', { fields: t('system.users.username') + '/' + t('system.users.Full name') })"
        />

        <!-- 表格 -->
        <!-- 要使用`el-table`组件原有的属性，直接加在Table标签上即可 -->
        <Table />

        <!-- 表单 -->
        <PopupForm />
    </div>
</template>

<script setup lang="ts">
import { provide } from 'vue'
import XaTableClass from '/@/utils/xaTable'
import PopupForm from './popupForm.vue'
import Table from '/@/components/table/index.vue'
import TableHeader from '/@/components/table/header/index.vue'
import { defaultOptButtons } from '/@/components/table'
import { useUserInfo } from '/@/stores/userInfo'
import { useI18n } from 'vue-i18n'
import { usersReadUsers, usersCreateUser, usersUpdateUser, usersDeleteUser } from '/@/client'

defineOptions({
    name: 'system/user',
})

const { t } = useI18n()
const userInfo = useUserInfo()

const optButtons = defaultOptButtons(['edit', 'delete'])
optButtons[1].display = (row) => {
    return row.id != userInfo.id
}

const xaTable = new XaTableClass(
    {
        queryKey: 'users',
        index: usersReadUsers,
        add: usersCreateUser,
        edit: usersUpdateUser,
        del: usersDeleteUser,
    },
    {
        column: [
            { type: 'selection', align: 'center', operator: false },
            {
                label: t('Id'),
                prop: 'id',
                propType: 'number',
                align: 'center',
                sortable: 'custom',
                operator: 'eq',
                operatorPlaceholder: t('Id'),
                width: 70,
            },
            { label: t('system.users.username'), prop: 'username', align: 'center', operator: 'LIKE', operatorPlaceholder: t('Fuzzy query') },
            { label: t('system.users.Full name'), prop: 'full_name', align: 'center', operator: 'LIKE', operatorPlaceholder: t('Fuzzy query') },
            {
                label: t('system.users.Roles'),
                prop: 'roles',
                align: 'center',
                operator: false,
                render: 'tags',
                formatter: (_row, _column, cellValue, _index) => {
                    return cellValue.map((item: anyObj) => item.name)
                },
                getRenderKey: (row, field, _column, index) => {
                    const renderKey =
                        index +
                        (field.render ? '-' + field.render : '') +
                        (field.prop ? '-' + field.prop + '-' + row[field.prop].map((item: anyObj) => [item.id, item.name].join('-')).join('-') : '')
                    return renderKey
                },
            },
            {
                label: t('system.users.Source'),
                prop: 'source',
                align: 'center',
                width: 100,
                render: 'tag',
                custom: { system: 'danger', signup: 'success' },
                replaceValue: { system: t('system.users.Source system'), signup: t('system.users.Source signup') },
            },
            {
                label: t('State'),
                prop: 'is_active',
                propType: 'boolean',
                align: 'center',
                width: 100,
                render: 'tag',
                custom: { false: 'warning', true: 'success' },
                replaceValue: { false: t('Disable'), true: t('Enable') },
            },
            {
                label: t('system.users.Superuser'),
                prop: 'is_superuser',
                propType: 'boolean',
                align: 'center',
                width: 100,
                render: 'tag',
                custom: { false: 'info', true: 'danger' },
                replaceValue: { false: t('No'), true: t('Yes') },
            },
            {
                label: t('system.users.Last login'),
                prop: 'last_login_at',
                align: 'center',
                render: 'datetime',
                sortable: 'custom',
                operator: 'RANGE',
                width: 160,
            },
            { label: t('Update time'), prop: 'updated_at', align: 'center', render: 'datetime', sortable: 'custom', operator: 'RANGE', width: 160 },
            { label: t('Create time'), prop: 'created_at', align: 'center', render: 'datetime', sortable: 'custom', operator: 'RANGE', width: 160 },

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
    {
        defaultItems: {
            is_active: true,
            is_superuser: false,
        },
    },
    {},
    {
        requestEdit: () => {
            xaTable.form.items!.roles = xaTable.form.items!.roles.map((item: any) => item.id)
        },
    }
)

provide('xaTable', xaTable)

xaTable.mount()
</script>

<style scoped lang="scss"></style>
