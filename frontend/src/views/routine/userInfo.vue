<template>
    <div class="default-main">
        <el-row :gutter="30">
            <el-col class="lg-mb-20" :xs="24" :sm="24" :md="24" :lg="10">
                <div class="user-info">
                    <el-image fit="cover" :src="fullUrl('/static/images/avatar.png')" class="avatar">
                        <template #error>
                            <div class="image-slot">
                                <Icon size="30" color="#c0c4cc" name="el-icon-Picture" />
                            </div>
                        </template>
                    </el-image>
                    <div class="user-info-base">
                        <div class="user-full-name">{{ state.userInfo.full_name }}</div>
                        <div class="user-other">
                            <div>{{ t('routine.userInfo.Last logged in on') }} {{ timeFormat(state.userInfo.last_login_at) }}</div>
                        </div>
                    </div>
                    <div class="user-info-form">
                        <el-form
                            @keyup.enter="onSubmit()"
                            :key="state.formKey"
                            label-position="top"
                            :rules="rules"
                            ref="formRef"
                            :model="state.userInfo"
                        >
                            <el-form-item :label="t('system.users.username')">
                                <el-input disabled v-model="state.userInfo.username"></el-input>
                            </el-form-item>
                            <el-form-item :label="t('system.users.Full name')" prop="full_name">
                                <el-input :placeholder="t('routine.userInfo.Please enter a full name')" v-model="state.userInfo.full_name"></el-input>
                            </el-form-item>
                            <el-form-item :label="t('routine.userInfo.New password')" prop="password">
                                <el-input
                                    type="password"
                                    :placeholder="t('routine.userInfo.Please leave blank if not modified')"
                                    v-model="state.userInfo.password"
                                ></el-input>
                            </el-form-item>
                            <el-form-item v-auth="'edit'">
                                <el-button type="primary" :loading="updateUserMeLoading" @click="onSubmit()">
                                    {{ t('routine.userInfo.Save changes') }}
                                </el-button>
                                <el-button @click="onResetForm(formRef)">{{ t('Reset') }}</el-button>
                            </el-form-item>
                        </el-form>
                    </div>
                </div>
            </el-col>
            <el-col v-loading="userOperationLogsLoading" :xs="24" :sm="24" :md="24" :lg="12">
                <el-card :header="t('routine.userInfo.Operation log')" shadow="never">
                    <el-timeline>
                        <el-timeline-item
                            v-for="(item, idx) in userOperationLogs?.data?.data"
                            :key="idx"
                            size="large"
                            :timestamp="timeFormat(item.created_at)"
                        >
                            {{ item.title }}
                        </el-timeline-item>
                    </el-timeline>
                    <el-pagination
                        v-model:current-page="state.logQuery.skip"
                        v-model:page-size="state.logQuery.limit"
                        :page-sizes="[12, 22, 52, 100]"
                        background
                        layout="prev, next, jumper"
                        :total="userOperationLogs?.data?.total ?? 0"
                    ></el-pagination>
                </el-card>
            </el-col>
        </el-row>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import type { FormInstance, FormItemRule } from 'element-plus'
import { fullUrl, onResetForm, timeFormat } from '/@/utils/common'
import { uuid } from '/@/utils/random'
import { buildValidatorData } from '/@/utils/validate'
import { useUserInfo } from '/@/stores/userInfo'
import { usersReadUserMe, usersReadUserOperationLogs, usersUpdateUserMe } from '/@/client'
import { useMutation, useQuery } from '@pinia/colada'
import { httpStatusHandle, isSuccess } from '/@/utils/request'

defineOptions({
    name: 'routine/userInfo',
})

const { t } = useI18n()
const formRef = ref<FormInstance>()

const userInfo = useUserInfo()

const state: {
    userInfo: anyObj
    formKey: string
    logQuery: anyObj
} = reactive({
    userInfo: {},
    formKey: uuid(),
    logQuery: {
        skip: 1,
        limit: 10,
    },
})

usersReadUserMe().then((res) => {
    state.userInfo = { ...res.data }
    // 重新渲染表单以记录初始值
    state.formKey = uuid()
})

const rules: Partial<Record<string, FormItemRule[]>> = reactive({
    full_name: [buildValidatorData({ name: 'required', title: t('system.users.Full name') })],
    password: [buildValidatorData({ name: 'password' })],
})

const { mutate: updateUserMeMutate, isLoading: updateUserMeLoading } = useMutation({
    mutation: () => usersUpdateUserMe({ body: { full_name: state.userInfo.full_name, password: state.userInfo.password } }),
    onSuccess: (data, _vars, _context) => {
        httpStatusHandle(data)
        const status = (data as anyObj).status
        if (status && typeof status === 'number' && isSuccess(status)) {
            userInfo.dataFill({ ...userInfo.$state, full_name: state.userInfo.full_name })
        }
    },
    onError: (error) => {
        console.error(error)
    },
})

const onSubmit = () => {
    if (!formRef.value) return
    formRef.value.validate((valid) => {
        if (valid) {
            updateUserMeMutate()
        }
    })
}

const { data: userOperationLogs, isLoading: userOperationLogsLoading } = useQuery({
    key: ['users', 'operation-logs', state.logQuery],
    query: () => usersReadUserOperationLogs({ query: state.logQuery }),
    placeholderData: (previousData) => previousData,
})
</script>

<style scoped lang="scss">
.user-info {
    background-color: var(--xa-bg-color-overlay);
    border-radius: var(--el-border-radius-base);
    border-top: 3px solid #409eff;
    .avatar {
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        margin: 60px auto 10px auto;
        border-radius: 50%;
        box-shadow: var(--el-box-shadow-light);
        border: 1px dashed var(--el-border-color);
        cursor: pointer;
        overflow: hidden;
        width: 110px;
        height: 110px;
    }
    .image-slot {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
    }
    .user-info-base {
        .user-full-name {
            font-size: 22px;
            color: var(--el-text-color-primary);
            text-align: center;
            padding: 8px 0;
        }
        .user-other {
            color: var(--el-text-color-regular);
            font-size: 14px;
            text-align: center;
            line-height: 20px;
        }
    }
    .user-info-form {
        padding: 30px;
    }
}
.el-card :deep(.el-timeline-item__icon) {
    font-size: 10px;
}
@media screen and (max-width: 1200px) {
    .lg-mb-20 {
        margin-bottom: 20px;
    }
}
</style>
