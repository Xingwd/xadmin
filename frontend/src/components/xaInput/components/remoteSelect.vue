<template>
    <div class="w100">
        <!-- el-select 的远程下拉只在有搜索词时，才会加载数据（显示出 option 列表） -->
        <!-- 使用 el-popover 在无数据/无搜索词时，显示一个无数据的提醒 -->
        <el-popover
            width="100%"
            placement="bottom"
            popper-class="remote-select-popper"
            :visible="state.focusStatus && !isLoading && !state.keyword && !remoteData.options.length"
            :teleported="false"
            :content="$t('utils.No data')"
            :hide-after="0"
        >
            <template #reference>
                <el-select
                    ref="selectRef"
                    class="w100"
                    remote
                    clearable
                    filterable
                    automatic-dropdown
                    remote-show-suffix
                    v-model="state.value"
                    :loading="isLoading"
                    :disabled="props.disabled"
                    @blur="onBlur"
                    @focus="onFocus"
                    @clear="onClear"
                    @change="onChangeSelect"
                    @keydown.esc.capture="onKeyDownEsc"
                    :remote-method="onRemoteMethod"
                    v-bind="$attrs"
                >
                    <el-option
                        class="remote-select-option"
                        v-for="item in remoteData.options"
                        :label="item[field]"
                        :value="item[state.primaryKey].toString()"
                        :key="item[state.primaryKey]"
                    >
                        <el-tooltip placement="right" effect="light" v-if="!isEmpty(tooltipParams)">
                            <template #content>
                                <p v-for="(tooltipParam, key) in tooltipParams" :key="key">{{ key }}: {{ item[tooltipParam] }}</p>
                            </template>
                            <div>{{ item[field] }}</div>
                        </el-tooltip>
                    </el-option>
                    <template v-if="remoteData.total && props.pagination" #footer>
                        <el-pagination
                            :currentPage="state.currentPage"
                            :page-size="state.pageSize"
                            :pager-count="5"
                            class="select-pagination"
                            :layout="props.paginationLayout"
                            :total="remoteData.total"
                            @current-change="onSelectCurrentPageChange"
                            :small="config.layout.shrink"
                        />
                    </template>
                </el-select>
            </template>
        </el-popover>
    </div>
</template>

<script lang="ts" setup>
import type { ElSelect } from 'element-plus'
import { isEmpty } from 'lodash-es'
import { computed, getCurrentInstance, nextTick, onMounted, onUnmounted, reactive, ref, toRaw, useAttrs, watch } from 'vue'
import { InputAttr } from '../index'
import { useConfig } from '/@/stores/config'
import { getArrayKey } from '/@/utils/common'
import { useQuery } from '@pinia/colada'

const attrs = useAttrs()
const config = useConfig()
const selectRef = ref<InstanceType<typeof ElSelect> | undefined>()
type ElSelectProps = Omit<Partial<InstanceType<typeof ElSelect>['$props']>, 'modelValue'>
type valueTypes = string | number | string[] | number[]

interface Props extends /* @vue-ignore */ ElSelectProps {
    pk?: string
    field?: string
    params?: anyObj
    remoteQueryKey: string
    remoteQuery: Function
    modelValue: valueTypes | null
    tooltipParams?: anyObj
    pagination?: boolean
    paginationLayout?: string
    labelFormatter?: (optionData: anyObj, optionKey: string) => string
    // 按下 ESC 键时直接使下拉框脱焦（默认是清理搜索词或关闭下拉面板，并且不会脱焦，造成 dialog 的按下 ESC 关闭失效）
    escBlur?: boolean
}
const props = withDefaults(defineProps<Props>(), {
    pk: 'id',
    field: 'name',
    params: () => {
        return {}
    },
    remoteQueryKey: '',
    remoteQuery: () => {},
    modelValue: '',
    tooltipParams: () => {
        return {}
    },
    pagination: true,
    paginationLayout: 'total, ->, prev, pager, next',
    disabled: false,
    escBlur: true,
})

/**
 * 点击清空按钮后的值，同时也是缺省值‌
 */
const valueOnClear = computed(() => {
    let valueOnClear = attrs.valueOnClear as InputAttr['valueOnClear']
    if (valueOnClear === undefined) {
        valueOnClear = attrs.multiple ? () => [] : () => null
    }
    return typeof valueOnClear == 'function' ? valueOnClear() : valueOnClear
})

/**
 * 被认为是空值的值列表
 */
const emptyValues = computed(() => (attrs.emptyValues as InputAttr['emptyValues']) || [null, undefined, ''])

const state: {
    // 主表字段名(不带表别名)
    primaryKey: string
    currentPage: number
    pageSize: number
    params: anyObj
    keyword: string
    value: valueTypes
    focusStatus: boolean
} = reactive({
    primaryKey: props.pk,
    currentPage: 1,
    pageSize: 10,
    params: props.params,
    keyword: '',
    value: valueOnClear.value,
    focusStatus: false,
})

const { data: remoteQueryData, isLoading } = useQuery({
    key: computed(() => {
        return [props.remoteQueryKey, state.keyword]
    }),
    query: () =>
        props.remoteQuery({
            query: {
                ...state.params,
                skip: state.currentPage,
                limit: state.pageSize,
                quick_search: state.keyword,
            },
        }),
    placeholderData: (previousData) => previousData,
})
const remoteData = computed(() => {
    let data = { options: [] as anyObj[], total: 0 }
    if ((remoteQueryData.value as anyObj)?.data) {
        let opts = (remoteQueryData.value as anyObj).data.data ? (remoteQueryData.value as anyObj).data.data : (remoteQueryData.value as anyObj).data
        if (typeof props.labelFormatter === 'function') {
            for (const key in opts) {
                opts[key][props.field] = props.labelFormatter(opts[key], key)
            }
        }
        data.options = opts
        data.total = (remoteQueryData.value as anyObj).data.total ?? 0
    }
    return data
})

let io: IntersectionObserver | null = null
const instance = getCurrentInstance()

const emits = defineEmits<{
    (e: 'update:modelValue', value: valueTypes): void
    (e: 'row', value: any): void
}>()

const onChangeSelect = (val: valueTypes) => {
    val = updateValue(val)
    if (typeof instance?.vnode.props?.onRow == 'function') {
        if (typeof val == 'number' || typeof val == 'string') {
            const dataKey = getArrayKey(remoteData.value.options, state.primaryKey, '' + val)
            emits('row', dataKey !== false ? toRaw(remoteData.value.options[dataKey]) : {})
        } else {
            const valueArr = []
            for (const key in val) {
                const dataKey = getArrayKey(remoteData.value.options, state.primaryKey, '' + val[key])
                if (dataKey !== false) {
                    valueArr.push(toRaw(remoteData.value.options[dataKey]))
                }
            }
            emits('row', valueArr)
        }
    }
}

const onKeyDownEsc = (e: KeyboardEvent) => {
    if (props.escBlur) {
        e.stopPropagation()
        selectRef.value?.blur()
    }
}

const onFocus = () => {
    state.focusStatus = true
}

const onClear = () => {
    // 点击清理按钮后，内部 input 呈聚焦状态，但选项面板不会展开，特此处理（element-plus@2.9.1）
    nextTick(() => {
        selectRef.value?.blur()
        selectRef.value?.focus()
    })
}

const onBlur = () => {
    state.keyword = ''
    state.focusStatus = false
}

const onRemoteMethod = (q: string) => {
    if (state.keyword != q) {
        state.keyword = q
        state.currentPage = 1
    }
}

const onSelectCurrentPageChange = (val: number) => {
    state.currentPage = val
}

const updateValue = (newVal: any) => {
    if (emptyValues.value.includes(newVal)) {
        state.value = valueOnClear.value
    } else {
        state.value = newVal

        // number[] 转 string[] 确保默认值能够选中
        if (typeof state.value === 'object') {
            for (const key in state.value) {
                state.value[key] = '' + state.value[key]
            }
        } else if (typeof state.value === 'number') {
            state.value = '' + state.value
        }
    }
    emits('update:modelValue', state.value)
    return state.value
}

onMounted(() => {
    // 去除主键中的表名
    let pkArr = props.pk.split('.')
    state.primaryKey = pkArr[pkArr.length - 1]

    // 初始化值
    updateValue(props.modelValue)

    setTimeout(() => {
        if (window?.IntersectionObserver) {
            io = new IntersectionObserver((entries) => {
                for (const key in entries) {
                    if (!entries[key].isIntersecting) selectRef.value?.blur()
                }
            })
            if (selectRef.value?.$el instanceof Element) {
                io.observe(selectRef.value.$el)
            }
        }
    }, 500)
})

onUnmounted(() => {
    io?.disconnect()
})

watch(
    () => props.modelValue,
    (newVal) => {
        /**
         * 防止 number 到 string 的类型转换触发默认值多次初始化
         * 相当于忽略数据类型进行比较 [1, 2] == ['1', '2']
         */
        if (getString(state.value) != getString(newVal)) {
            updateValue(newVal)
        }
    }
)

const getString = (val: valueTypes | null) => {
    // 确保 [] 和 '' 的返回值不一样
    return `${typeof val}:${String(val)}`
}

const getRef = () => {
    return selectRef.value
}

const focus = () => {
    selectRef.value?.focus()
}

const blur = () => {
    selectRef.value?.blur()
}

defineExpose({
    blur,
    focus,
    getRef,
})
</script>

<style scoped lang="scss">
:deep(.remote-select-popper) {
    color: var(--el-text-color-secondary);
    font-size: 12px;
    text-align: center;
}
.remote-select-option {
    white-space: pre;
}
</style>
