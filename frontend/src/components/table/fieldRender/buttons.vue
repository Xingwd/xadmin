<template>
    <div v-memo="[field]">
        <template v-for="(btn, idx) in field.buttons" :key="idx">
            <template v-if="btn.display ? btn.display(row, field) : true">
                <!-- 常规按钮 -->
                <el-button
                    v-if="btn.render == 'basicButton'"
                    v-blur
                    @click="onButtonClick(btn)"
                    :class="btn.class"
                    class="xa-table-render-buttons-item"
                    :type="btn.type"
                    :disabled="btn.disabled && btn.disabled(row, field)"
                    v-bind="btn.attr"
                >
                    <Icon v-if="btn.icon" :name="btn.icon" />
                    <div v-if="btn.text" class="text">{{ getTranslation(btn.text) }}</div>
                </el-button>

                <!-- 带提示信息的按钮 -->
                <el-tooltip
                    v-if="btn.render == 'tipButton' && ((btn.name == 'edit' && xaTable.auth('edit')) || btn.name != 'edit')"
                    :disabled="btn.title && !btn.disabledTip ? false : true"
                    :content="getTranslation(btn.title)"
                    placement="top"
                >
                    <el-button
                        v-blur
                        @click="onButtonClick(btn)"
                        :class="btn.class"
                        class="xa-table-render-buttons-item"
                        :type="btn.type"
                        :disabled="btn.disabled && btn.disabled(row, field)"
                        v-bind="btn.attr"
                    >
                        <Icon v-if="btn.icon" :name="btn.icon" />
                        <div v-if="btn.text" class="text">{{ getTranslation(btn.text) }}</div>
                    </el-button>
                </el-tooltip>

                <!-- 带确认框的按钮 -->
                <el-popconfirm
                    v-if="btn.render == 'confirmButton' && ((btn.name == 'delete' && xaTable.auth('del')) || btn.name != 'delete')"
                    :disabled="btn.disabled && btn.disabled(row, field)"
                    v-bind="btn.popconfirm"
                    @confirm="onButtonClick(btn)"
                >
                    <template #reference>
                        <div class="ml-6">
                            <el-tooltip :disabled="btn.title ? false : true" :content="getTranslation(btn.title)" placement="top">
                                <el-button
                                    v-blur
                                    :class="btn.class"
                                    class="xa-table-render-buttons-item"
                                    :type="btn.type"
                                    :disabled="btn.disabled && btn.disabled(row, field)"
                                    v-bind="btn.attr"
                                >
                                    <Icon v-if="btn.icon" :name="btn.icon" />
                                    <div v-if="btn.text" class="text">{{ getTranslation(btn.text) }}</div>
                                </el-button>
                            </el-tooltip>
                        </div>
                    </template>
                </el-popconfirm>
            </template>
        </template>
    </div>
</template>

<script setup lang="ts">
import { TableColumnCtx } from 'element-plus'
import { inject } from 'vue'
import { useI18n } from 'vue-i18n'
import type XaTableClass from '/@/utils/xaTable'

interface Props {
    row: TableRow
    field: TableColumn
    column: TableColumnCtx<TableRow>
    index: number
}

const { t, te } = useI18n()
const props = defineProps<Props>()
const xaTable = inject('xaTable') as XaTableClass

const onButtonClick = (btn: OptButton) => {
    if (typeof btn.click === 'function') {
        btn.click(props.row, props.field)
        return
    }
    xaTable.onTableAction(btn.name, props)
}

const getTranslation = (key?: string) => {
    if (!key) return ''
    return te(key) ? t(key) : key
}
</script>

<style scoped lang="scss">
.xa-table-render-buttons-item {
    padding: 4px 5px;
    height: auto;
    .icon {
        font-size: 14px !important;
        color: var(--xa-bg-color-overlay) !important;
    }
    .text {
        padding-left: 5px;
    }
}
.xa-table-render-buttons-move {
    cursor: move;
}
.ml-6 {
    display: inline-flex;
    vertical-align: middle;
    margin-left: 6px;
}
.ml-6 + .el-button {
    margin-left: 6px;
}
</style>
