<template>
    <!-- 通用搜索 -->
    <transition name="el-zoom-in-bottom" mode="out-in">
        <CommonSearch v-show="props.buttons.includes('commonSearch') && xaTable.table.showCommonSearch">
            <template v-for="(slot, idx) in $slots" :key="idx" #[idx]>
                <slot :name="idx"></slot>
            </template>
        </CommonSearch>
    </transition>

    <!-- 操作按钮组 -->
    <div v-bind="$attrs" class="table-header xa-scroll-style">
        <slot name="refreshPrepend"></slot>
        <el-tooltip v-if="props.buttons.includes('refresh')" :content="t('Refresh')" placement="top">
            <el-button v-blur @click="onAction('refresh', { loading: true })" color="#40485b" class="table-header-operate" type="info">
                <Icon name="fa fa-refresh" />
            </el-button>
        </el-tooltip>
        <slot name="refreshAppend"></slot>
        <el-tooltip v-if="props.buttons.includes('add') && xaTable.auth('add')" :content="t('Add')" placement="top">
            <el-button v-blur @click="onAction('add')" class="table-header-operate" type="primary">
                <Icon name="fa fa-plus" />
                <span class="table-header-operate-text">{{ t('Add') }}</span>
            </el-button>
        </el-tooltip>
        <el-tooltip v-if="props.buttons.includes('edit') && xaTable.auth('edit')" :content="t('Edit selected row')" placement="top">
            <el-button v-blur @click="onAction('edit')" :disabled="!enableBatchOpt" class="table-header-operate" type="primary">
                <Icon name="fa fa-pencil" />
                <span class="table-header-operate-text">{{ t('Edit') }}</span>
            </el-button>
        </el-tooltip>
        <el-popconfirm
            v-if="props.buttons.includes('delete') && xaTable.auth('del')"
            @confirm="onAction('delete')"
            :confirm-button-text="t('Delete')"
            :cancel-button-text="t('Cancel')"
            confirmButtonType="danger"
            :title="t('Are you sure to delete the selected record?')"
            :disabled="!enableBatchOpt"
        >
            <template #reference>
                <div class="mlr-12">
                    <el-tooltip :content="t('Delete selected row')" placement="top">
                        <el-button v-blur :disabled="!enableBatchOpt" class="table-header-operate" type="danger">
                            <Icon name="fa fa-trash" />
                            <span class="table-header-operate-text">{{ t('Delete') }}</span>
                        </el-button>
                    </el-tooltip>
                </div>
            </template>
        </el-popconfirm>
        <el-tooltip
            v-if="props.buttons.includes('unfold')"
            :content="(xaTable.table.expandAll ? t('Shrink') : t('Open')) + t('All submenus')"
            placement="top"
        >
            <el-button
                v-blur
                @click="xaTable.onTableHeaderAction('unfold', { unfold: !xaTable.table.expandAll })"
                class="table-header-operate"
                :type="xaTable.table.expandAll ? 'danger' : 'warning'"
            >
                <span class="table-header-operate-text">{{ xaTable.table.expandAll ? t('Shrink all') : t('Expand all') }}</span>
            </el-button>
        </el-tooltip>

        <!-- slot -->
        <slot></slot>

        <!-- 右侧搜索框和工具按钮 -->
        <div class="table-search">
            <slot name="quickSearchPrepend"></slot>
            <el-input
                v-if="props.buttons.includes('quickSearch')"
                v-model="state.quickSearch"
                class="xs-hidden quick-search"
                @input="onSearchInput"
                :placeholder="quickSearchPlaceholder ? quickSearchPlaceholder : t('Search')"
                clearable
            />
            <div class="table-search-button-group" v-if="props.buttons.includes('columnDisplay') || props.buttons.includes('commonSearch')">
                <el-dropdown v-if="props.buttons.includes('columnDisplay')" :max-height="380" :hide-on-click="false">
                    <el-button
                        class="table-search-button-item"
                        :class="props.buttons.includes('commonSearch') ? 'right-border' : ''"
                        color="#dcdfe6"
                        plain
                        v-blur
                    >
                        <Icon size="14" name="el-icon-Grid" />
                    </el-button>
                    <template #dropdown>
                        <el-dropdown-menu>
                            <el-dropdown-item v-for="(item, idx) in columnDisplay" :key="idx">
                                <el-checkbox
                                    v-if="item.prop"
                                    @change="onChangeShowColumn($event, item.prop!)"
                                    :checked="!item.show"
                                    :model-value="item.show"
                                    size="small"
                                    :label="item.label"
                                />
                            </el-dropdown-item>
                        </el-dropdown-menu>
                    </template>
                </el-dropdown>
                <el-tooltip
                    v-if="props.buttons.includes('commonSearch')"
                    :disabled="xaTable.table.showCommonSearch"
                    :content="t('Expand generic search')"
                    placement="top"
                >
                    <el-button
                        class="table-search-button-item"
                        @click="xaTable.table.showCommonSearch = !xaTable.table.showCommonSearch"
                        color="#dcdfe6"
                        plain
                        v-blur
                    >
                        <Icon size="14" name="el-icon-Search" />
                    </el-button>
                </el-tooltip>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { debounce } from 'lodash-es'
import { computed, inject, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import CommonSearch from '/@/components/table/commonSearch/index.vue'
import type XaTableClass from '/@/utils/xaTable'

const { t } = useI18n()
const xaTable = inject('xaTable') as XaTableClass

interface Props {
    buttons: HeaderOptButton[]
    quickSearchPlaceholder?: string
}
const props = withDefaults(defineProps<Props>(), {
    buttons: () => {
        return ['refresh', 'add', 'edit', 'delete']
    },
    quickSearchPlaceholder: '',
})

const state: {
    quickSearch: string
} = reactive({
    quickSearch: '',
})

const columnDisplay = computed(() => {
    let columnDisplayArr = []
    for (let item of xaTable.table.column) {
        item.type === 'selection' || item.render === 'buttons' || item.enableColumnDisplayControl === false ? '' : columnDisplayArr.push(item)
    }
    return columnDisplayArr
})

const enableBatchOpt = computed(() => (xaTable.table.selection!.length > 0 ? true : false))

const onAction = (event: string, data: anyObj = {}) => {
    xaTable.onTableHeaderAction(event, data)
}

const onSearchInput = debounce(() => {
    xaTable.table.query!.quick_search = state.quickSearch
}, 800)

const onChangeShowColumn = (value: string | number | boolean, field: string) => {
    xaTable.onTableHeaderAction('change-show-column', { field: field, value: value })
}
</script>

<style scoped lang="scss">
.table-header {
    position: relative;
    overflow-x: auto;
    box-sizing: border-box;
    display: flex;
    align-items: center;
    width: 100%;
    max-width: 100%;
    background-color: var(--xa-bg-color-overlay);
    border: 1px solid var(--xa-border-color);
    border-bottom: none;
    padding: 13px 15px;
    font-size: 14px;
    .table-header-operate-text {
        margin-left: 6px;
    }
}

.mlr-12 {
    margin-left: 12px;
}
.mlr-12 + .el-button {
    margin-left: 12px;
}
.table-search {
    display: flex;
    margin-left: auto;
    .quick-search {
        width: auto;
    }
}
.table-search-button-group {
    display: flex;
    margin-left: 12px;
    border: 1px solid var(--el-border-color);
    border-radius: var(--el-border-radius-base);
    overflow: hidden;
    button:focus,
    button:active {
        background-color: var(--xa-bg-color-overlay);
    }
    button:hover {
        background-color: var(--el-color-info-light-7);
    }
    .table-search-button-item {
        height: 30px;
        border: none;
        border-radius: 0;
    }
    .el-button + .el-button {
        margin: 0;
    }
    .right-border {
        border-right: 1px solid var(--el-border-color);
    }
}

html.dark {
    .table-search-button-group {
        button:focus,
        button:active {
            background-color: var(--el-color-info-dark-2);
        }
        button:hover {
            background-color: var(--el-color-info-light-7);
        }
        button {
            background-color: var(--xa-bg-color-overlay);
            el-icon {
                color: white !important;
            }
        }
    }
}
</style>
