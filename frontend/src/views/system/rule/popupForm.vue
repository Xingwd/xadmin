<template>
    <!-- 对话框表单 -->
    <el-dialog
        class="xa-operate-dialog"
        :close-on-click-modal="false"
        :destroy-on-close="true"
        :model-value="['Add', 'Edit'].includes(xaTable.form.operate!)"
        @close="xaTable.toggleForm"
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
                    <FormItem
                        type="remoteSelect"
                        prop="parent_id"
                        :label="t('system.rules.Superior menu rule')"
                        v-model="xaTable.form.items!.parent_id"
                        :placeholder="t('Click select')"
                        :input-attr="{
                            field: 'title',
                            params: { only_menus: true },
                            remoteQueryKey: 'rules',
                            remoteQuery: rulesReadRules,
                        }"
                    />
                    <FormItem
                        :label="t('system.rules.Rule type')"
                        v-model="xaTable.form.items!.type"
                        type="radio"
                        :input-attr="{
                            border: true,
                            content: {
                                menu_dir: t('system.rules.type menu_dir'),
                                menu_item: t('system.rules.type menu_item'),
                                permission: t('system.rules.type permission'),
                            },
                        }"
                    />
                    <el-form-item prop="title" :label="t('system.rules.Rule title')">
                        <el-input
                            v-model="xaTable.form.items!.title"
                            type="string"
                            :placeholder="t('Please input field', { field: t('system.rules.Rule title') })"
                        ></el-input>
                    </el-form-item>
                    <FormItem
                        v-if="xaTable.form.items!.type == 'permission'"
                        type="remoteSelect"
                        prop="name"
                        :label="t('system.rules.Rule name')"
                        v-model="xaTable.form.items!.name"
                        :placeholder="t('Click select')"
                        :input-attr="{
                            pk: 'name',
                            field: 'name',
                            params: { unassigned: true },
                            remoteQueryKey: 'rules/permissions',
                            remoteQuery: rulesReadPermissions,
                        }"
                        :attr="{
                            blockHelp: t(
                                'system.rules.It will be registered as a frontend route name and used for frontend and backend authentication'
                            ),
                        }"
                    />
                    <el-form-item v-else prop="name" :label="t('system.rules.Rule name')">
                        <el-input
                            v-model="xaTable.form.items!.name"
                            type="string"
                            :placeholder="t('system.rules.English name, such as system/rules')"
                        ></el-input>
                        <div class="block-help">
                            {{ t('system.rules.It will be registered as a frontend route name and used for frontend and backend authentication') }}
                        </div>
                    </el-form-item>
                    <el-form-item v-if="xaTable.form.items!.type != 'permission'" :label="t('system.rules.Routing path')">
                        <el-input
                            v-model="xaTable.form.items!.path"
                            type="string"
                            :placeholder="t('system.rules.The frontend routing path (path) does not need to start with `/`, such as system/rules')"
                        ></el-input>
                    </el-form-item>
                    <FormItem
                        v-if="xaTable.form.operate && xaTable.form.items!.type != 'permission'"
                        type="icon"
                        :label="t('system.rules.Rule Icon')"
                        v-model="xaTable.form.items!.icon"
                        :input-attr="{
                            showIconName: true,
                        }"
                    />
                    <FormItem
                        v-if="xaTable.form.items!.type == 'menu_item'"
                        :label="t('system.rules.Menu type')"
                        v-model="xaTable.form.items!.menu_item_type"
                        type="radio"
                        :input-attr="{
                            border: true,
                            content: { tab: t('system.rules.Menu type tab'), link: t('system.rules.Menu type link (offsite)'), iframe: 'Iframe' },
                        }"
                    />
                    <el-form-item
                        prop="url"
                        v-if="xaTable.form.items!.menu_item_type != 'tab' && xaTable.form.items!.type != 'permission'"
                        :label="t('system.rules.Link address')"
                    >
                        <el-input
                            v-model="xaTable.form.items!.url"
                            type="string"
                            :placeholder="t('system.rules.Please enter the URL address of the link or iframe')"
                        ></el-input>
                    </el-form-item>
                    <el-form-item
                        v-if="xaTable.form.items!.type == 'menu_item' && xaTable.form.items!.menu_item_type == 'tab'"
                        :label="t('system.rules.Component path')"
                    >
                        <el-input
                            v-model="xaTable.form.items!.component"
                            type="string"
                            :placeholder="t('system.rules.Frontend component path, please start with /src, such as: /src/views/home')"
                        ></el-input>
                    </el-form-item>
                    <el-form-item :label="t('system.rules.Rule comments')">
                        <el-input
                            @keyup.enter.stop=""
                            @keyup.ctrl.enter="xaTable.onSubmit(formRef)"
                            v-model="xaTable.form.items!.remark"
                            type="textarea"
                            :autosize="{ minRows: 2, maxRows: 5 }"
                            :placeholder="
                                t(
                                    'system.rules.You can obtain this value by CurrentRoute meta remark for use, such as the banner text on the homepage'
                                )
                            "
                        ></el-input>
                    </el-form-item>
                    <el-form-item :label="t('system.rules.Rule weight')">
                        <el-input
                            v-model="xaTable.form.items!.weight"
                            type="number"
                            :placeholder="t('system.rules.Please enter the weight of menu rule (sort by)')"
                        ></el-input>
                    </el-form-item>
                    <FormItem
                        :label="t('Cache')"
                        v-model="xaTable.form.items!.cache"
                        type="radio"
                        :input-attr="{
                            border: true,
                            content: { false: t('Disable'), true: t('Enable') },
                        }"
                    />
                    <FormItem
                        :label="t('State')"
                        v-model="xaTable.form.items!.status"
                        type="radio"
                        :input-attr="{
                            border: true,
                            content: { false: t('Disable'), true: t('Enable') },
                        }"
                    />
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
</template>

<script setup lang="ts">
import { reactive, ref, inject } from 'vue'
import { useI18n } from 'vue-i18n'
import type XaTableClass from '/@/utils/xaTable'
import FormItem from '/@/components/formItem/index.vue'
import { buildValidatorData } from '/@/utils/validate'
import type { FormInstance, FormItemRule } from 'element-plus'
import { useConfig } from '/@/stores/config'
import { rulesReadRules, rulesReadPermissions } from '/@/client'

const config = useConfig()
const formRef = ref<FormInstance>()
const xaTable = inject('xaTable') as XaTableClass

const { t } = useI18n()

const rules: Partial<Record<string, FormItemRule[]>> = reactive({
    title: [buildValidatorData({ name: 'required', title: t('system.rules.Rule title') })],
    name: [buildValidatorData({ name: 'required', title: t('system.rules.Rule name') })],
    url: [buildValidatorData({ name: 'url', message: t('system.rules.Please enter the correct URL') })],
    parent_id: [
        {
            validator: (_rule: any, val: string, callback: Function) => {
                if (!val) {
                    return callback()
                }
                if (parseInt(val) == parseInt(xaTable.form.items!.id)) {
                    return callback(new Error(t('system.rules.The superior menu rule cannot be the rule itself')))
                }
                return callback()
            },
            trigger: 'blur',
        },
    ],
})
</script>

<style scoped lang="scss"></style>
