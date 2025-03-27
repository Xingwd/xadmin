<template>
    <div>
        <slot name="neck"></slot>
        <el-table
            ref="tableRef"
            class="xa-data-table w100"
            header-cell-class-name="table-header-cell"
            :default-expand-all="xaTable.table.expandAll"
            :data="queryData.data"
            :row-key="xaTable.table.pk"
            :border="true"
            v-loading="indexQueryIsLoading"
            stripe
            @select-all="onSelectAll"
            @select="onSelect"
            @selection-change="onSelectionChange"
            @sort-change="onSortChange"
            @row-dblclick="xaTable.onTableDblclick"
            v-bind="$attrs"
        >
            <slot name="columnPrepend"></slot>
            <template v-for="(item, key) in xaTable.table.column">
                <template v-if="item.show !== false">
                    <!-- 渲染为 slot -->
                    <slot v-if="item.render == 'slot'" :name="item.slotName"></slot>

                    <el-table-column
                        v-else
                        :key="key + '-column'"
                        v-bind="item"
                        :column-key="(item['columnKey'] ? item['columnKey'] : `table-column-${item.prop}`) || shortUuid()"
                    >
                        <!-- ./fieldRender/ 文件夹内的每个组件为一种字段渲染器，组件名称为渲染器名称 -->
                        <template v-if="item.render" #default="scope">
                            <component
                                :row="scope.row"
                                :field="item"
                                :column="scope.column"
                                :index="scope.$index"
                                :is="fieldRenderer[item.render] ?? fieldRenderer['default']"
                                :key="getRenderKey(key, item, scope)"
                            />
                        </template>
                    </el-table-column>
                </template>
            </template>
            <slot name="columnAppend"></slot>
        </el-table>
        <div v-if="props.pagination" class="table-pagination">
            <el-pagination
                v-model:current-page="xaTable.table.query!.skip"
                v-model:page-size="xaTable.table.query!.limit"
                :page-sizes="pageSizes"
                background
                :layout="config.layout.shrink ? 'prev, next, jumper' : 'sizes,total, ->, prev, pager, next, jumper'"
                :total="queryData.total"
            ></el-pagination>
        </div>
        <slot name="footer"></slot>
    </div>
</template>

<script setup lang="ts">
import type { ElTable, TableInstance } from 'element-plus'
import type { Component } from 'vue'
import { computed, inject, nextTick, ref } from 'vue'
import { useConfig } from '/@/stores/config'
import type XaTableClass from '/@/utils/xaTable'
import { shortUuid } from '/@/utils/random'

const config = useConfig()
const tableRef = ref<TableInstance>()
const xaTable = inject('xaTable') as XaTableClass
const { data: indexQueryData, isLoading: indexQueryIsLoading } = xaTable.indexQueryReturn
const queryData = computed(() => {
    return {
        data: (indexQueryData.value as anyObj)?.data.data,
        total: (indexQueryData.value as anyObj)?.data.total ?? 0,
    }
})
type ElTableProps = Partial<InstanceType<typeof ElTable>['$props']>

interface Props extends /* @vue-ignore */ ElTableProps {
    pagination?: boolean
}
const props = withDefaults(defineProps<Props>(), {
    pagination: true,
})

const fieldRenderer: Record<string, Component> = {}
const fieldRendererComponents: Record<string, any> = import.meta.glob('./fieldRender/**.vue', { eager: true })
for (const key in fieldRendererComponents) {
    const fileName = key.replace('./fieldRender/', '').replace('.vue', '')
    fieldRenderer[fileName] = fieldRendererComponents[key].default
}

const getRenderKey = (key: number, item: TableColumn, scope: any) => {
    if (item.getRenderKey && typeof item.getRenderKey == 'function') {
        return item.getRenderKey(scope.row, item, scope.column, scope.$index)
    }
    return key + scope.$index + '-' + item.render + '-' + (item.prop ? '-' + item.prop + '-' + scope.row[item.prop] : '')
}

const onSortChange = ({ order, prop }: { order: string; prop: string }) => {
    xaTable.onTableAction('sort-change', { order_by: prop, order_direction: order ? (order == 'ascending' ? 'asc' : 'desc') : '' })
}

const pageSizes = computed(() => {
    let defaultSizes = [10, 20, 50, 100]
    if (xaTable.table.query!.limit) {
        if (!defaultSizes.includes(xaTable.table.query!.limit)) {
            defaultSizes.push(xaTable.table.query!.limit)
        }
    }
    return defaultSizes
})

/*
 * 全选和取消全选
 * 实现子级同时选择和取消选中
 */
const onSelectAll = (selection: TableRow[]) => {
    if (isSelectAll(selection.map((row: TableRow) => row[xaTable.table.pk!].toString()))) {
        selection.map((row: TableRow) => {
            if (row.children) {
                selectChildren(row.children, true)
            }
        })
    } else {
        tableRef.value?.clearSelection()
    }
}

/*
 * 是否是全选操作
 * 只检查第一个元素是否被选择
 * 全选时：selectIds为所有元素的id
 * 取消全选时：selectIds为所有子元素的id
 */
const isSelectAll = (selectIds: string[]) => {
    let data = queryData.value.data as TableRow[]
    for (const key in data) {
        return selectIds.includes(data[key][xaTable.table.pk!].toString())
    }
    return false
}

/*
 * 选择子项-递归
 */
const selectChildren = (children: TableRow[], type: boolean) => {
    children.map((j: TableRow) => {
        toggleSelection(j, type)
        if (j.children) {
            selectChildren(j.children, type)
        }
    })
}

/*
 * 执行选择操作
 */
const toggleSelection = (row: TableRow, type: boolean) => {
    if (row) {
        nextTick(() => {
            tableRef.value?.toggleRowSelection(row, type)
        })
    }
}

/*
 * 手动选择时，同时选择子级
 */
const onSelect = (selection: TableRow[], row: TableRow) => {
    if (
        selection.some((item: TableRow) => {
            return row[xaTable.table.pk!] === item[xaTable.table.pk!]
        })
    ) {
        if (row.children) {
            selectChildren(row.children, true)
        }
    } else {
        if (row.children) {
            selectChildren(row.children, false)
        }
    }
}

/*
 * 记录选择的项
 */
const onSelectionChange = (selection: TableRow[]) => {
    xaTable.onTableAction('selection-change', selection)
}

/*
 * 设置折叠所有-递归
 */
const setUnFoldAll = (children: TableRow[], unfold: boolean) => {
    for (const key in children) {
        tableRef.value?.toggleRowExpansion(children[key], unfold)
        if (children[key].children) {
            setUnFoldAll(children[key].children!, unfold)
        }
    }
}

/*
 * 折叠所有
 */
const unFoldAll = (unfold: boolean) => {
    setUnFoldAll(queryData.value.data, unfold)
}

const getRef = () => {
    return tableRef.value
}

defineExpose({
    unFoldAll,
    getRef,
})
</script>

<style scoped lang="scss">
.xa-data-table :deep(.el-button + .el-button) {
    margin-left: 6px;
}
.xa-data-table :deep(.table-header-cell) .cell {
    color: var(--el-text-color-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.table-pagination {
    box-sizing: border-box;
    width: 100%;
    max-width: 100%;
    background-color: var(--xa-bg-color-overlay);
    padding: 13px 15px;
}
</style>
