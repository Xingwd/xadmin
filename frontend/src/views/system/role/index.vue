<template>
    <div class="default-main xa-table-box">
        <!-- 表格顶部菜单 -->
        <TableHeader
            :buttons="['refresh', 'add', 'edit', 'delete', 'quickSearch', 'columnDisplay']"
            :quick-search-placeholder="t('Quick search placeholder', { fields: t('system.roles.Role name') })"
        />

        <!-- 表格 -->
        <!-- 要使用`el-table`组件原有的属性，直接加在Table标签上即可 -->
        <Table :pagination="false" />

        <!-- 表单 -->
        <PopupForm ref="formRef" />
    </div>
</template>

<script setup lang="ts">
import { cloneDeep } from 'lodash-es'
import { provide, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import PopupForm from './popupForm.vue'
import { defaultOptButtons } from '/@/components/table'
import TableHeader from '/@/components/table/header/index.vue'
import Table from '/@/components/table/index.vue'
import XaTableClass from '/@/utils/xaTable'
import { uuid } from '/@/utils/random'
import { rolesReadRoles, rolesCreateRole, rolesUpdateRole, rolesDeleteRole } from '/@/client'

defineOptions({
    name: 'system/role',
})

const formRef = ref()
const { t } = useI18n()
let optButtons: OptButton[] = [
    {
        render: 'tipButton',
        name: 'info',
        title: 'Info',
        text: '',
        type: 'info',
        icon: 'fa fa-search-plus',
        class: 'table-row-info',
        disabledTip: false,
        click: (row: TableRow) => {
            infoButtonClick(row)
        },
    },
]
optButtons = optButtons.concat(defaultOptButtons(['edit', 'delete']))

const xaTable = new XaTableClass(
    {
        queryKey: 'roles',
        index: rolesReadRoles,
        add: rolesCreateRole,
        edit: rolesUpdateRole,
        del: rolesDeleteRole,
    },
    {
        column: [
            { type: 'selection', align: 'center' },
            { label: t('system.roles.Role name'), prop: 'name', align: 'left', width: '200' },
            {
                label: t('system.roles.Permissions'),
                prop: 'permissions',
                align: 'center',
                formatter: (_row, _column, cellValue, _index) => {
                    return Array.isArray(cellValue) && cellValue.length > 0 ? (cellValue[0]?.title || '未知') + '等 ' + cellValue.length + ' 项' : ''
                },
            },
            {
                label: t('system.roles.Users'),
                prop: 'users',
                align: 'center',
                formatter: (_row, _column, cellValue, _index) => {
                    return Array.isArray(cellValue) && cellValue.length > 0 ? '共 ' + cellValue.length + ' 个' : ''
                },
            },
            { label: t('Update time'), prop: 'updated_at', align: 'center', width: '160', render: 'datetime' },
            { label: t('Create time'), prop: 'created_at', align: 'center', width: '160', render: 'datetime' },
            { label: t('Operate'), align: 'center', width: '130', render: 'buttons', buttons: optButtons },
        ],
    },
    {},
    {
        onTableDblclick: ({ row }) => {
            infoButtonClick(row)
            return false
        },
        // 提交前
        onSubmit: () => {
            xaTable.form.items!.permissions = formRef.value.getCheckeds()
            return true
        },
    },
    {
        // 切换表单后
        toggleForm({ operate }) {
            if (operate == 'Add') {
                ruleTreeUpdate()
            }
        },
        // 编辑请求完成后
        requestEdit: () => {
            ruleTreeUpdate()
            xaTable.form.items!.users = xaTable.form.items!.users.map((item: any) => item.id)
        },
    }
)

/** 点击查看详情按钮响应 */
const infoButtonClick = (row: TableRow) => {
    if (!row) return
    // 数据来自表格数据,未重新请求api,深克隆,不然可能会影响表格
    let rowClone = cloneDeep(row)
    xaTable.form.extend!.info = rowClone
    xaTable.form.operate = 'Info'
}

const ruleTreeUpdate = () => {
    if (xaTable.form.items!.permissions && xaTable.form.items!.permissions.length) {
        xaTable.form.extend!.defaultCheckedKeys = processDefaultCheckedKeys(xaTable.form.items!.permissions)
    } else {
        xaTable.form.extend!.defaultCheckedKeys = []
    }
    xaTable.form.extend!.treeKey = uuid()
}

const processDefaultCheckedKeys = (permissions: anyObj[]) => {
    const parentIds = new Set<number>()

    permissions.forEach((item) => {
        if (item.parent_id) {
            parentIds.add(item.parent_id)
        }
    })

    return permissions.filter((item: any) => !parentIds.has(item.id)).map((item: any) => item.id)
}

provide('xaTable', xaTable)

xaTable.mount()
</script>

<style scoped lang="scss"></style>
