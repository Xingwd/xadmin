<template>
    <!-- 新增/编辑表单 -->
    <el-dialog
        class="xa-operate-dialog"
        :close-on-click-modal="false"
        :model-value="['Add', 'Edit'].includes(xaTable.form.operate!)"
        @close="xaTable.toggleForm"
        :destroy-on-close="true"
    >
        <template #header>
            <div class="title" v-drag="['.xa-operate-dialog', '.el-dialog__header']" v-zoom="'.xa-operate-dialog'">
                {{ xaTable.form.operate ? t(xaTable.form.operate) : '' }}
            </div>
        </template>
        <el-scrollbar v-loading="xaTable.form.loading" class="xa-table-form-scrollbar">
            <div
                class="xa-operate-form"
                :class="'xa-' + xaTable.form.operate + '-form'"
                :style="config.layout.shrink ? '' : 'width: calc(100% - ' + xaTable.form.labelWidth! / 2 + 'px)'"
            >
                <el-form
                    ref="formRef"
                    @keyup.enter="xaTable.onSubmit(formRef)"
                    :model="xaTable.form.items"
                    :label-position="config.layout.shrink ? 'top' : 'right'"
                    :label-width="xaTable.form.labelWidth + 'px'"
                    :rules="rules"
                    v-if="!xaTable.form.loading"
                >
                    <el-form-item prop="name" :label="t('system.roles.Role name')">
                        <el-input
                            v-model="xaTable.form.items!.name"
                            type="string"
                            :placeholder="t('Please input field', { field: t('system.roles.Role name') })"
                        ></el-input>
                    </el-form-item>
                    <FormItem
                        type="remoteSelect"
                        prop="users"
                        :label="t('system.roles.User list')"
                        v-model="xaTable.form.items!.users"
                        :input-attr="{
                            field: 'username',
                            remoteQueryKey: 'users',
                            remoteQuery: usersReadUsers,
                            multiple: true,
                            placeholder: t('Click select'),
                        }"
                    />
                    <el-form-item prop="permissions" :label="t('system.roles.Permissions')">
                        <el-tree
                            ref="treeRef"
                            :key="xaTable.form.extend!.treeKey"
                            :default-checked-keys="xaTable.form.extend!.defaultCheckedKeys"
                            :default-expand-all="true"
                            show-checkbox
                            node-key="id"
                            :props="{ children: 'children', label: 'title', class: treeNodeClass }"
                            :data="ruleTrees?.data?.data"
                            class="w100"
                        />
                    </el-form-item>
                </el-form>
            </div>
        </el-scrollbar>
        <template #footer>
            <div :style="'width: calc(100% - ' + xaTable.form.labelWidth! / 1.8 + 'px)'">
                <el-button @click="xaTable.toggleForm('')">{{ t('Cancel') }}</el-button>
                <el-button v-blur :loading="xaTable.form.submitLoading" @click="xaTable.onSubmit(formRef)" type="primary">
                    {{ xaTable.form.operateRows && xaTable.form.operateRows.length > 1 ? t('Save and edit next item') : t('Save') }}
                </el-button>
            </div>
        </template>
    </el-dialog>
    <!-- 查看详情 -->
    <el-dialog class="xa-operate-dialog" :model-value="xaTable.form.operate === 'Info'" @close="xaTable.toggleForm" :destroy-on-close="true">
        <template #header>
            <div class="title" v-drag="['.xa-operate-dialog', '.el-dialog__header']" v-zoom="'.xa-operate-dialog'">{{ t('Info') }}</div>
        </template>
        <el-scrollbar v-loading="xaTable.form.loading" class="xa-table-form-scrollbar">
            <div class="xa-operate-form" :class="'xa-' + xaTable.form.operate + '-form'">
                <el-descriptions :title="t('Basic information')" :column="4" border>
                    <el-descriptions-item :label="t('Id')">
                        {{ xaTable.form.extend!.info.id }}
                    </el-descriptions-item>
                    <el-descriptions-item :label="t('system.roles.Role name')">
                        {{ xaTable.form.extend!.info.name }}
                    </el-descriptions-item>
                    <el-descriptions-item :label="t('Create time')">
                        {{ timeFormat(xaTable.form.extend!.info.created_at) }}
                    </el-descriptions-item>
                    <el-descriptions-item :label="t('Update time')">
                        {{ timeFormat(xaTable.form.extend!.info.updated_at) }}
                    </el-descriptions-item>
                </el-descriptions>
                <el-descriptions :title="t('system.roles.User list')" :column="2" border style="margin-top: 20px" />
                <el-table :data="xaTable.form.extend!.info.users" style="width: 100%">
                    <el-table-column prop="id" :label="t('Id')" width="100" />
                    <el-table-column prop="username" :label="t('Name')" />
                </el-table>
                <el-descriptions :title="t('system.roles.Permission list')" :column="2" border style="margin-top: 20px" />
                <el-table :data="xaTable.form.extend!.info.permissions" style="width: 100%">
                    <el-table-column prop="id" :label="t('Id')" width="100" />
                    <el-table-column prop="name" :label="t('Name')" />
                    <el-table-column prop="title" :label="t('Title')" />
                </el-table>
            </div>
        </el-scrollbar>
    </el-dialog>
</template>

<script setup lang="ts">
import { reactive, ref, inject } from 'vue'
import { useI18n } from 'vue-i18n'
import type XaTableClass from '/@/utils/xaTable'
import type { FormInstance, ElTree, FormItemRule } from 'element-plus'
import FormItem from '/@/components/formItem/index.vue'
import { buildValidatorData } from '/@/utils/validate'
import { timeFormat } from '/@/utils/common'
import type Node from 'element-plus/es/components/tree/src/model/node'
import { useConfig } from '/@/stores/config'
import { usersReadUsers, rulesReadRules } from '/@/client'
import { useQuery } from '@pinia/colada'

const config = useConfig()
const formRef = ref<FormInstance>()
const treeRef = ref<InstanceType<typeof ElTree>>()
const xaTable = inject('xaTable') as XaTableClass

const { t } = useI18n()

const rules: Partial<Record<string, FormItemRule[]>> = reactive({
    name: [buildValidatorData({ name: 'required', title: t('system.roles.Role name') })],
})

const { data: ruleTrees } = useQuery({
    key: ['rules'],
    query: () => rulesReadRules(),
    placeholderData: (previousData) => previousData,
})

const getCheckeds = () => {
    return treeRef.value!.getCheckedKeys().concat(treeRef.value!.getHalfCheckedKeys())
}

const treeNodeClass = (_data: anyObj, node: Node) => {
    if (node.isLeaf) return ''
    let addClass = true
    for (const key in node.childNodes) {
        if (!node.childNodes[key].isLeaf) {
            addClass = false
        }
    }
    return addClass ? 'penultimate-node' : ''
}

defineExpose({
    getCheckeds,
})
</script>

<style scoped lang="scss">
:deep(.penultimate-node) {
    .el-tree-node__children {
        padding-left: 60px;
        white-space: pre-wrap;
        line-height: 12px;
        .el-tree-node {
            display: inline-block;
        }
        .el-tree-node__content {
            padding-left: 5px !important;
            padding-right: 5px;
            .el-tree-node__expand-icon {
                display: none;
            }
        }
    }
}
</style>
