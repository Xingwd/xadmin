<template>
    <!-- 对话框表单 -->
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
                    <FormItem
                        :label="t('system.users.username')"
                        v-model="xaTable.form.items!.username"
                        type="string"
                        prop="username"
                        :placeholder="t('system.users.User login name')"
                    />
                    <FormItem
                        :label="t('system.users.Password')"
                        prop="password"
                        v-model="xaTable.form.items!.password"
                        type="password"
                        :placeholder="
                            xaTable.form.operate == 'Add'
                                ? t('Please input field', { field: t('system.users.Password') })
                                : t('system.users.Please leave blank if not modified')
                        "
                    />
                    <FormItem
                        :label="t('system.users.Full name')"
                        v-model="xaTable.form.items!.full_name"
                        type="string"
                        prop="full_name"
                        :placeholder="t('Please input field', { field: t('system.users.Full name') })"
                    />
                    <FormItem
                        :label="t('State')"
                        v-model="xaTable.form.items!.is_active"
                        type="radio"
                        :input-attr="{
                            border: true,
                            content: { false: t('Disable'), true: t('Enable') },
                        }"
                    />
                    <FormItem
                        :label="t('system.users.Superuser')"
                        v-model="xaTable.form.items!.is_superuser"
                        type="switch"
                        :input-attr="{
                            border: true,
                        }"
                    />
                    <FormItem
                        type="remoteSelect"
                        prop="roles"
                        :label="t('system.users.Role list')"
                        v-model="xaTable.form.items!.roles"
                        :placeholder="t('Click select')"
                        :input-attr="{
                            remoteQueryKey: 'roles',
                            remoteQuery: rolesReadRoles,
                            multiple: true,
                            placeholder: t('Click select'),
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
import { ref, reactive, inject, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type XaTableClass from '/@/utils/xaTable'
import { regularPassword, buildValidatorData } from '/@/utils/validate'
import type { FormInstance, FormItemRule } from 'element-plus'
import FormItem from '/@/components/formItem/index.vue'
import { useConfig } from '/@/stores/config'
import { rolesReadRoles } from '/@/client'

const config = useConfig()
const formRef = ref<FormInstance>()
const xaTable = inject('xaTable') as XaTableClass

const { t } = useI18n()

const rules: Partial<Record<string, FormItemRule[]>> = reactive({
    username: [buildValidatorData({ name: 'required', title: t('system.users.username') }), buildValidatorData({ name: 'account' })],
    password: [
        {
            validator: (_rule: any, val: string, callback: Function) => {
                if (xaTable.form.operate == 'Add') {
                    if (!val) {
                        return callback(new Error(t('Please input field', { field: t('system.users.Password') })))
                    }
                } else {
                    if (!val) {
                        return callback()
                    }
                }
                if (!regularPassword(val)) {
                    return callback(new Error(t('validate.Please enter the correct password')))
                }
                return callback()
            },
            trigger: 'blur',
        },
    ],
})

watch(
    () => xaTable.form.operate,
    (newVal) => {
        rules.password![0].required = newVal == 'Add'
    }
)
</script>

<style scoped lang="scss">
.avatar-uploader {
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    border-radius: var(--el-border-radius-small);
    box-shadow: var(--el-box-shadow-light);
    border: 1px dashed var(--el-border-color);
    cursor: pointer;
    overflow: hidden;
    width: 110px;
    height: 110px;
}
.avatar-uploader:hover {
    border-color: var(--el-color-primary);
}
.avatar {
    width: 110px;
    height: 110px;
    display: block;
}
.image-slot {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
}
</style>
