<template>
    <!-- 查看详情 -->
    <el-dialog class="xa-operate-dialog" :model-value="xaTable.form.operate ? true : false" @close="xaTable.toggleForm">
        <template #header>
            <div class="title" v-drag="['.xa-operate-dialog', '.el-dialog__header']" v-zoom="'.xa-operate-dialog'">{{ t('Info') }}</div>
        </template>
        <el-scrollbar v-loading="xaTable.form.loading" class="xa-table-form-scrollbar">
            <div class="xa-operate-form" :class="'xa-' + xaTable.form.operate + '-form'">
                <el-descriptions :column="2" border>
                    <el-descriptions-item :label="t('Id')">
                        {{ xaTable.form.extend!.info.id }}
                    </el-descriptions-item>
                    <el-descriptions-item :label="t('system.operationLogs.user_id')">
                        {{ xaTable.form.extend!.info.user_id }}
                    </el-descriptions-item>
                    <el-descriptions-item :label="t('Create time')">
                        {{ timeFormat(xaTable.form.extend!.info.create_time) }}
                    </el-descriptions-item>
                    <el-descriptions-item :label="t('system.operationLogs.username')">
                        {{ xaTable.form.extend!.info.username }}
                    </el-descriptions-item>
                    <el-descriptions-item :width="120" :span="2" :label="t('Title')">
                        {{ xaTable.form.extend!.info.title }}
                    </el-descriptions-item>
                    <el-descriptions-item :width="120" :span="2" :label="t('system.operationLogs.Request Method')">
                        {{ xaTable.form.extend!.info.request_method }}
                    </el-descriptions-item>
                    <el-descriptions-item :width="120" :span="2" :label="t('system.operationLogs.Request Path')">
                        {{ xaTable.form.extend!.info.request_path }}
                    </el-descriptions-item>
                    <el-descriptions-item :width="120" :span="2" :label="t('system.operationLogs.Request Query Params')">
                        <el-tree class="table-el-tree" :data="xaTable.form.extend!.info.data" :props="{ label: 'label', children: 'children' }" />
                    </el-descriptions-item>
                    <el-descriptions-item :width="120" :span="2" :label="t('system.operationLogs.Response Status Code')">
                        {{ xaTable.form.extend!.info.response_status_code }}
                    </el-descriptions-item>
                </el-descriptions>
            </div>
        </el-scrollbar>
    </el-dialog>
</template>

<script setup lang="ts">
import { inject } from 'vue'
import { useI18n } from 'vue-i18n'
import type XaTableClass from '/@/utils/xaTable'
import { timeFormat } from '/@/utils/common'

const { t } = useI18n()
const xaTable = inject('xaTable') as XaTableClass
</script>

<style scoped lang="scss">
.table-el-tree {
    :deep(.el-tree-node) {
        white-space: unset;
    }
    :deep(.el-tree-node__content) {
        display: block;
        align-items: unset;
        height: unset;
    }
}
</style>
