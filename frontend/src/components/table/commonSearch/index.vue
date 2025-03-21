<template>
    <div class="table-common-search">
        <el-form @submit.prevent="" @keyup.enter="xaTable.onTableAction('common-search', {})" label-position="top" :model="xaTable.commonSearch.form">
            <el-row>
                <template v-for="(item, idx) in xaTable.table.column" :key="idx">
                    <template v-if="item.operator !== false">
                        <!-- 自定义渲染 component、slot -->
                        <el-col
                            v-if="item.commonSearchRender == 'customRender' || item.commonSearchRender == 'slot'"
                            v-bind="{
                                xs: item.commonSearchColAttr?.xs ? item.commonSearchColAttr?.xs : 24,
                                sm: item.commonSearchColAttr?.sm ? item.commonSearchColAttr?.sm : 6,
                                ...item.commonSearchColAttr,
                            }"
                        >
                            <!-- 外部可以使用 :deep() 选择器修改css样式 -->
                            <div class="common-search-col" :class="item.prop">
                                <div class="common-search-col-label" v-if="item.commonSearchShowLabel !== false">{{ item.label }}</div>
                                <div class="common-search-col-input">
                                    <!-- 自定义组件/函数渲染 -->
                                    <component
                                        v-if="item.commonSearchRender == 'customRender'"
                                        :is="item.commonSearchCustomRender"
                                        :renderRow="item"
                                        :renderField="item.prop!"
                                        :renderValue="xaTable.commonSearch.form[item.prop!]"
                                    />

                                    <!-- 自定义渲染-slot -->
                                    <slot v-else-if="item.commonSearchRender == 'slot'" :name="item.commonSearchSlotName"></slot>
                                </div>
                            </div>
                        </el-col>

                        <!-- 时间范围 -->
                        <el-col v-else-if="item.render == 'datetime' && (item.operator == 'RANGE' || item.operator == 'NOT RANGE')" :xs="24" :sm="12">
                            <div class="common-search-col" :class="item.prop">
                                <div class="common-search-col-label w16" v-if="item.commonSearchShowLabel !== false">{{ item.label }}</div>
                                <div class="common-search-col-input-range w83">
                                    <el-date-picker
                                        class="datetime-picker w100"
                                        v-model="xaTable.commonSearch.form[item.prop!]"
                                        :default-time="[new Date(2000, 1, 1, 0, 0, 0), new Date(2000, 1, 1, 23, 59, 59)]"
                                        :type="item.commonSearchRender == 'date' ? 'daterange' : 'datetimerange'"
                                        :range-separator="$t('To')"
                                        :start-placeholder="$t('el.datepicker.startDate')"
                                        :end-placeholder="$t('el.datepicker.endDate')"
                                        :value-format="item.commonSearchRender == 'date' ? 'YYYY-MM-DD' : 'YYYY-MM-DD HH:mm:ss'"
                                        :teleported="false"
                                    />
                                </div>
                            </div>
                        </el-col>
                        <el-col v-else :xs="24" :sm="6">
                            <div class="common-search-col" :class="item.prop">
                                <div class="common-search-col-label" v-if="item.commonSearchShowLabel !== false">{{ item.label }}</div>
                                <!-- 数字范围 -->
                                <div v-if="item.operator == 'RANGE' || item.operator == 'NOT RANGE'" class="common-search-col-input-range">
                                    <el-input
                                        :placeholder="item.operatorPlaceholder"
                                        type="string"
                                        v-model="xaTable.commonSearch.form[item.prop! + '-start']"
                                        :clearable="true"
                                    ></el-input>
                                    <div class="range-separator">{{ $t('To') }}</div>
                                    <el-input
                                        :placeholder="item.operatorPlaceholder"
                                        type="string"
                                        v-model="xaTable.commonSearch.form[item.prop! + '-end']"
                                        :clearable="true"
                                    ></el-input>
                                </div>
                                <!-- 是否 [NOT] NULL -->
                                <div v-else-if="item.operator == 'NULL' || item.operator == 'NOT NULL'" class="common-search-col-input">
                                    <el-checkbox v-model="xaTable.commonSearch.form[item.prop!]" :label="item.operator" size="large"></el-checkbox>
                                </div>
                                <div v-else-if="item.operator" class="common-search-col-input">
                                    <!-- 时间筛选 -->
                                    <el-date-picker
                                        class="datetime-picker w100"
                                        v-if="item.render == 'datetime' || item.commonSearchRender == 'date'"
                                        v-model="xaTable.commonSearch.form[item.prop!]"
                                        :type="item.commonSearchRender == 'date' ? 'date' : 'datetime'"
                                        :value-format="item.commonSearchRender == 'date' ? 'YYYY-MM-DD' : 'YYYY-MM-DD HH:mm:ss'"
                                        :placeholder="item.operatorPlaceholder"
                                        :teleported="false"
                                    />

                                    <!-- tag、tags、select -->
                                    <el-select
                                        class="w100"
                                        :placeholder="item.operatorPlaceholder"
                                        v-else-if="
                                            (item.render == 'tag' || item.render == 'tags' || item.commonSearchRender == 'select') &&
                                            item.replaceValue
                                        "
                                        v-model="xaTable.commonSearch.form[item.prop!]"
                                        :multiple="item.operator == 'IN' || item.operator == 'NOT IN'"
                                        :clearable="true"
                                    >
                                        <el-option v-for="(opt, okey) in item.replaceValue" :key="item.prop! + okey" :label="opt" :value="okey" />
                                    </el-select>

                                    <!-- 远程 select -->
                                    <XaInput
                                        v-else-if="item.commonSearchRender == 'remoteSelect'"
                                        type="remoteSelect"
                                        v-model="xaTable.commonSearch.form[item.prop!]"
                                        :attr="item.remote"
                                        :placeholder="item.operatorPlaceholder"
                                    />

                                    <!-- 开关 -->
                                    <el-select
                                        :placeholder="item.operatorPlaceholder"
                                        v-else-if="item.render == 'switch'"
                                        v-model="xaTable.commonSearch.form[item.prop!]"
                                        :clearable="true"
                                        class="w100"
                                    >
                                        <template v-if="!isEmpty(item.replaceValue)">
                                            <el-option v-for="(opt, okey) in item.replaceValue" :key="item.prop! + okey" :label="opt" :value="okey" />
                                        </template>
                                        <template v-else>
                                            <el-option :label="$t('utils.open')" value="1" />
                                            <el-option :label="$t('utils.close')" value="0" />
                                        </template>
                                    </el-select>

                                    <!-- 数字 -->
                                    <el-input
                                        :placeholder="item.operatorPlaceholder"
                                        v-else-if="item.propType == 'number'"
                                        type="number"
                                        v-model="xaTable.commonSearch.form[item.prop!]"
                                        :clearable="true"
                                    ></el-input>

                                    <!-- 字符串 -->
                                    <el-input
                                        :placeholder="item.operatorPlaceholder"
                                        v-else
                                        type="string"
                                        v-model="xaTable.commonSearch.form[item.prop!]"
                                        :clearable="true"
                                    ></el-input>
                                </div>
                            </div>
                        </el-col>
                    </template>
                </template>
                <el-col :xs="24" :sm="6">
                    <div class="common-search-col pl-20">
                        <el-button v-blur @click="xaTable.onTableAction('common-search', {})" type="primary">{{ $t('Search') }}</el-button>
                        <el-button @click="onResetForm()">{{ $t('Reset') }}</el-button>
                    </div>
                </el-col>
            </el-row>
        </el-form>
    </div>
</template>

<script setup lang="ts">
import { inject } from 'vue'
import type XaTableClass from '/@/utils/xaTable'
import { isEmpty } from 'lodash-es'
import XaInput from '/@/components/xaInput/index.vue'

const xaTable = inject('xaTable') as XaTableClass

const onResetForm = () => {
    /**
     * 封装好的 /utils/common.js/onResetForm 工具在此处不能使用，因为未使用 el-form-item
     * 改用通用搜索重新初始化函数
     */
    xaTable.initCommonSearch()

    // 通知 xaTable 发起通用搜索
    xaTable.onTableAction('common-search', {})
}
</script>

<style scoped lang="scss">
.table-common-search {
    box-sizing: border-box;
    width: 100%;
    max-width: 100%;
    background-color: var(--xa-bg-color-overlay);
    border: 1px solid var(--xa-border-color);
    border-bottom: none;
    padding: 13px 15px;
    font-size: 14px;
    .common-search-col {
        display: flex;
        align-items: center;
        padding-top: 8px;
        color: var(--el-text-color-regular);
        font-size: 13px;
    }
    .common-search-col-label {
        width: 33.33%;
        padding: 0 15px;
        text-align: right;
        overflow: hidden;
        white-space: nowrap;
    }
    .common-search-col-input {
        padding: 0 15px;
        width: 66.66%;
    }
    .common-search-col-input-range {
        display: flex;
        align-items: center;
        padding: 0 15px;
        width: 66.66%;
        .range-separator {
            padding: 0 5px;
        }
    }
}
.pl-20 {
    padding-left: 20px;
}
.w16 {
    width: 16.5% !important;
}
.w83 {
    width: 83.5% !important;
}
</style>
