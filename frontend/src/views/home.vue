<template>
    <div class="default-main">
        <div class="banner">
            <el-row :gutter="10">
                <el-col :lg="18">
                    <div class="welcome suspension">
                        <img class="welcome-img" :src="headerSvg" alt="" />
                        <div>
                            <div class="welcome-title">
                                {{ (userInfo.full_name ? userInfo.full_name : userInfo.username) + t('utils.comma') + getGreet() }}
                            </div>
                            <div class="welcome-note">{{ state.remark }}</div>
                        </div>
                    </div>
                </el-col>
                <el-col :lg="6">
                    <div class="working">
                        <img class="working-coffee" :src="coffeeSvg" alt="" />
                        <div class="working-text">
                            {{ t('home.You have worked today') }}<span class="time">{{ state.workingTimeFormat }}</span>
                        </div>
                        <div @click="onChangeWorkState()" class="working-opt">
                            {{ state.pauseWork ? t('home.Continue to work') : t('home.have a bit of rest') }}
                        </div>
                    </div>
                </el-col>
            </el-row>
        </div>
        <el-divider content-position="left" class="x-divider x-divider__text">{{ t('home.Frequently used menus') }}</el-divider>
        <div class="general-panel-box">
            <el-row :gutter="20">
                <el-col v-for="item in menus" :key="item.name" :xs="8" :sm="6" :md="6" :lg="3" class="general-panel">
                    <el-tooltip :content="(item.meta as anyObj).full_title" placement="top">
                        <el-button @click="onClickMenu(item)" plain class="general-panel-content suspension">
                            <Icon :color="config.getColorVal('menuColor')" :name="item.meta?.icon" style="margin-right: 5px" />
                            {{ item.meta?.title }}
                        </el-button>
                    </el-tooltip>
                </el-col>
            </el-row>
        </div>
        <el-divider content-position="left" class="x-divider x-divider__text">{{ t('home.Behavioral statistics') }}</el-divider>
        <div class="small-panel-box">
            <el-row :gutter="20">
                <el-col v-for="(item, index) in statistics" :key="index" :md="12" :lg="6">
                    <div class="small-panel suspension">
                        <div class="small-panel-title">{{ item.title }}</div>
                        <div class="small-panel-content">
                            <div class="content-left">
                                <Icon :color="item.icon.color" size="20" :name="item.icon.name" />
                                <el-statistic :value="item.value.value" :value-style="statisticValueStyle" />
                            </div>
                            <div class="content-right">
                                <el-text :type="item.valueOn.value == 0 ? '' : item.valueOn.value > 0 ? 'danger' : 'success'">
                                    <span v-if="item.valueOn.value > 0">+</span>{{ Math.round(item.valueOn.value) }}%
                                </el-text>
                            </div>
                        </div>
                    </div>
                </el-col>
            </el-row>
        </div>
        <div class="growth-chart">
            <el-row :gutter="20">
                <el-col class="lg-mb-20" :lg="8">
                    <el-card shadow="hover" :header="t('home.Recent 1 Week Behavior Trend')" class="suspension">
                        <G2Chart class="user-behavior-chart" :options="behavior1WOptions" />
                    </el-card>
                </el-col>
                <el-col class="lg-mb-20" :lg="16">
                    <el-card shadow="hover" :header="t('home.Recent 1 Month Behavior Trend')" class="suspension">
                        <G2Chart class="user-behavior-chart" :options="behavior1MOptions" />
                    </el-card>
                </el-col>
            </el-row>
        </div>
    </div>
</template>

<script setup lang="ts">
import { useTransition } from '@vueuse/core'
import { CSSProperties, computed, onMounted, onUnmounted, reactive, toRefs } from 'vue'
import { useI18n } from 'vue-i18n'
import coffeeSvg from '/@/assets/home/coffee.svg'
import headerSvg from '/@/assets/home/header-1.svg'
import { useUserInfo } from '/@/stores/userInfo'
import { WORKING_TIME } from '/@/stores/constant/cacheKey'
import { getGreet } from '/@/utils/common'
import { Local } from '/@/utils/storage'
import G2Chart from '/@/components/antv/g2Chart.vue'
import { useConfig } from '/@/stores/config'
import { useNavTabs } from '/@/stores/navTabs'
import { RouteRecordRaw } from 'vue-router'
import { useQuery } from '@pinia/colada'
import { usersReadUserHome } from '/@/client'
import { onClickMenu } from '/@/utils/router'

let workTimer: number

defineOptions({
    name: 'home',
})

const d = new Date()
const { t } = useI18n()
const config = useConfig()
const navTabs = useNavTabs()
const userInfo = useUserInfo()

const state: {
    remark: string
    workingTimeFormat: string
    pauseWork: boolean
} = reactive({
    remark: t('home.Loading'),
    workingTimeFormat: '',
    pauseWork: false,
})

state.remark = navTabs.state.activeRoute?.meta.remark as string

onMounted(() => {
    startWork()
})

onUnmounted(() => {
    clearInterval(workTimer)
})

const onChangeWorkState = () => {
    const time = parseInt((new Date().getTime() / 1000).toString())
    const workingTime = Local.get(WORKING_TIME)
    if (state.pauseWork) {
        // 继续工作
        workingTime.pauseTime += time - workingTime.startPauseTime
        workingTime.startPauseTime = 0
        Local.set(WORKING_TIME, workingTime)
        state.pauseWork = false
        startWork()
    } else {
        // 暂停工作
        workingTime.startPauseTime = time
        Local.set(WORKING_TIME, workingTime)
        clearInterval(workTimer)
        state.pauseWork = true
    }
}

const startWork = () => {
    const workingTime = Local.get(WORKING_TIME) || { date: '', startTime: 0, pauseTime: 0, startPauseTime: 0 }
    const currentDate = d.getFullYear() + '-' + (d.getMonth() + 1) + '-' + d.getDate()
    const time = parseInt((new Date().getTime() / 1000).toString())

    if (workingTime.date != currentDate) {
        workingTime.date = currentDate
        workingTime.startTime = time
        workingTime.pauseTime = workingTime.startPauseTime = 0
        Local.set(WORKING_TIME, workingTime)
    }

    let startPauseTime = 0
    if (workingTime.startPauseTime <= 0) {
        state.pauseWork = false
        startPauseTime = 0
    } else {
        state.pauseWork = true
        startPauseTime = time - workingTime.startPauseTime // 已暂停时间
    }

    let workingSeconds = time - workingTime.startTime - workingTime.pauseTime - startPauseTime

    state.workingTimeFormat = formatSeconds(workingSeconds)
    if (!state.pauseWork) {
        workTimer = window.setInterval(() => {
            workingSeconds++
            state.workingTimeFormat = formatSeconds(workingSeconds)
        }, 1000)
    }
}

const formatSeconds = (seconds: number) => {
    var secondTime = 0 // 秒
    var minuteTime = 0 // 分
    var hourTime = 0 // 小时
    var dayTime = 0 // 天
    var result = ''

    if (seconds < 60) {
        secondTime = seconds
    } else {
        // 获取分钟，除以60取整数，得到整数分钟
        minuteTime = Math.floor(seconds / 60)
        // 获取秒数，秒数取佘，得到整数秒数
        secondTime = Math.floor(seconds % 60)
        // 如果分钟大于60，将分钟转换成小时
        if (minuteTime >= 60) {
            // 获取小时，获取分钟除以60，得到整数小时
            hourTime = Math.floor(minuteTime / 60)
            // 获取小时后取佘的分，获取分钟除以60取佘的分
            minuteTime = Math.floor(minuteTime % 60)
            if (hourTime >= 24) {
                // 获取天数， 获取小时除以24，得到整数天
                dayTime = Math.floor(hourTime / 24)
                // 获取小时后取余小时，获取分钟除以24取余的分；
                hourTime = Math.floor(hourTime % 24)
            }
        }
    }

    result =
        hourTime +
        t('home.hour') +
        ((minuteTime >= 10 ? minuteTime : '0' + minuteTime) + t('home.minute')) +
        ((secondTime >= 10 ? secondTime : '0' + secondTime) + t('home.second'))
    if (dayTime > 0) {
        result = dayTime + t('home.day') + result
    }
    return result
}

const { data } = useQuery({
    key: ['users', 'home'],
    query: () => usersReadUserHome(),
    placeholderData: (previousData) => previousData,
})

const homeData = computed(() => {
    return {
        logins_1w: data.value?.data?.logins_1w ?? 0,
        previous_logins_1w: data.value?.data?.previous_logins_1w ?? 0,
        logins_1m: data.value?.data?.logins_1m ?? 0,
        previous_logins_1m: data.value?.data?.previous_logins_1m ?? 0,
        operations_1w: data.value?.data?.operations_1w ?? 0,
        previous_operations_1w: data.value?.data?.previous_operations_1w ?? 0,
        operations_1m: data.value?.data?.operations_1m ?? 0,
        previous_operations_1m: data.value?.data?.previous_operations_1m ?? 0,
        behavior_1w: data.value?.data?.behavior_1w ?? [],
        behavior_1m: data.value?.data?.behavior_1m ?? [],
        menus: data.value?.data?.menus ?? [],
    }
})

const buildRouteMap = (routes: RouteRecordRaw[], title_prefix: string | undefined = undefined, routeMap: Map<string, any> = new Map()) => {
    routes.forEach((item: any) => {
        item.meta!.full_title = title_prefix ? title_prefix + ' / ' + item.meta.title : item.meta.title
        routeMap.set(item.name, item)
        if (item.children && item.children.length) {
            buildRouteMap(item.children, item.meta.full_title, routeMap)
        }
    })
    return routeMap
}

const routeMap = computed(() => buildRouteMap(navTabs.state.tabsViewRoutes))

const menus = computed(() => {
    const menusData: RouteRecordRaw[] = []

    homeData.value.menus.forEach((item: anyObj) => {
        const route = routeMap.value.get(item.menu)
        if (route && route.meta) {
            menusData.push(route)
        }
    })
    return menusData
})

const getRatio = (current: number, previous: number) => {
    return previous > 0 ? ((current - previous) / previous) * 100 : 0
}

const statistics = computed(() => {
    /**
     * 带有数字向上变化特效的数据
     */
    const countUp = reactive({
        logins1W: 0,
        loginsWow: 0,
        logins1M: 0,
        loginsMom: 0,
        operations1W: 0,
        operationsWow: 0,
        operations1M: 0,
        operationsMom: 0,
    })
    const countUpRefs = toRefs(countUp)

    const logins1WOutput = useTransition(countUpRefs.logins1W, { duration: 1500 })
    const loginsWowOutput = useTransition(countUpRefs.loginsWow, { duration: 1500 })
    const logins1MOutput = useTransition(countUpRefs.logins1M, { duration: 1500 })
    const loginsMomOutput = useTransition(countUpRefs.loginsMom, { duration: 1500 })
    const operations1WOutput = useTransition(countUpRefs.operations1W, { duration: 1500 })
    const operationsWowOutput = useTransition(countUpRefs.operationsWow, { duration: 1500 })
    const operations1MOutput = useTransition(countUpRefs.operations1M, { duration: 1500 })
    const operationsMomOutput = useTransition(countUpRefs.operationsMom, { duration: 1500 })

    countUpRefs.logins1W.value = homeData.value.logins_1w
    countUpRefs.loginsWow.value = getRatio(homeData.value.logins_1w, homeData.value.previous_logins_1w)
    countUpRefs.logins1M.value = homeData.value.logins_1m
    countUpRefs.loginsMom.value = getRatio(homeData.value.logins_1m, homeData.value.previous_logins_1m)
    countUpRefs.operations1W.value = homeData.value.operations_1w
    countUpRefs.operationsWow.value = getRatio(homeData.value.operations_1w, homeData.value.previous_operations_1w)
    countUpRefs.operations1M.value = homeData.value.operations_1m
    countUpRefs.operationsMom.value = getRatio(homeData.value.operations_1m, homeData.value.previous_operations_1m)

    return [
        {
            title: t('home.Recent 1 Week Logins'),
            icon: {
                color: '#8595F4',
                name: 'el-icon-Stamp',
            },
            value: logins1WOutput,
            valueOn: loginsWowOutput,
        },
        {
            title: t('home.Recent 1 Week Operations'),
            icon: {
                color: '#74A8B5',
                name: 'el-icon-Pointer',
            },
            value: operations1WOutput,
            valueOn: operationsWowOutput,
        },
        {
            title: t('home.Recent 1 Month Logins'),
            icon: {
                color: '#AD85F4',
                name: 'el-icon-Stamp',
            },
            value: logins1MOutput,
            valueOn: loginsMomOutput,
        },
        {
            title: t('home.Recent 1 Month Operations'),
            icon: {
                color: '#F48595',
                name: 'el-icon-Pointer',
            },
            value: operations1MOutput,
            valueOn: operationsMomOutput,
        },
    ]
})

const statisticValueStyle: CSSProperties = {
    fontSize: '28px',
}

const buildBehaviorOptions = (data: anyObj[]) => {
    return {
        type: 'view',
        autoFit: true,
        data: data,
        encode: { x: 'dt', y: 'count', color: 'behavior' },
        axis: { x: { title: '日期' }, y: { title: '次数' } },
        legend: {
            color: {
                layout: {
                    justifyContent: 'center',
                },
            },
        },
        children: [
            { type: 'line', encode: { shape: 'smooth' } },
            { type: 'point', encode: { shape: 'point' }, tooltip: false },
        ],
    }
}

const behavior1WOptions = computed(() => {
    return buildBehaviorOptions(homeData.value.behavior_1w)
})
const behavior1MOptions = computed(() => {
    return buildBehaviorOptions(homeData.value.behavior_1m)
})
</script>

<style scoped lang="scss">
.welcome {
    background: #e1eaf9;
    border-radius: 6px;
    display: flex;
    align-items: center;
    padding: 15px 20px !important;
    box-shadow: 0 0 30px 0 rgba(82, 63, 105, 0.05);
    .welcome-img {
        height: 100px;
        margin-right: 10px;
        user-select: none;
    }
    .welcome-title {
        font-size: 1.5rem;
        line-height: 30px;
        color: var(--xa-color-primary-light);
    }
    .welcome-note {
        padding-top: 6px;
        font-size: 15px;
        color: var(--el-text-color-primary);
    }
}
.working {
    height: 130px;
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    height: 100%;
    position: relative;
    &:hover {
        .working-coffee {
            -webkit-transform: translateY(-4px) scale(1.02);
            -moz-transform: translateY(-4px) scale(1.02);
            -ms-transform: translateY(-4px) scale(1.02);
            -o-transform: translateY(-4px) scale(1.02);
            transform: translateY(-4px) scale(1.02);
            z-index: 999;
        }
    }
    .working-coffee {
        transition: all 0.3s ease;
        width: 80px;
    }
    .working-text {
        display: block;
        width: 100%;
        font-size: 15px;
        text-align: center;
        color: var(--el-text-color-primary);
    }
    .working-opt {
        position: absolute;
        top: -40px;
        right: 10px;
        background-color: rgba($color: #000000, $alpha: 0.3);
        padding: 10px 20px;
        border-radius: 20px;
        color: var(--xa-bg-color-overlay);
        transition: all 0.3s ease;
        cursor: pointer;
        opacity: 0;
        z-index: 999;
        &:active {
            background-color: rgba($color: #000000, $alpha: 0.6);
        }
    }
    &:hover {
        .working-opt {
            opacity: 1;
            top: 0;
        }
    }
}

.x-divider {
    margin-top: 30px;
    margin-bottom: 30px;
}

.x-divider__text :deep(.el-divider__text) {
    background-color: var(--xa-bg-color);
}

.general-panel-box {
    min-height: 32px;
}

.general-panel {
    display: flex;
    align-items: center;
    justify-content: center;
    .general-panel-content {
        min-width: 120px;
        margin-top: 10px;
        margin-bottom: 10px;
    }
}

.small-panel-box {
    margin-top: 20px;
}
.small-panel {
    background-color: #e9edf2;
    border-radius: var(--el-border-radius-base);
    padding: 18px;
    margin-bottom: 20px;
    .small-panel-title {
        color: #92969a;
        font-size: 15px;
    }
    .small-panel-content {
        display: flex;
        align-items: flex-end;
        margin-top: 20px;
        color: #2c3f5d;
        .content-left {
            display: flex;
            align-items: center;
            font-size: 24px;
            .icon {
                margin-right: 10px;
            }
        }
        .content-right {
            font-size: 18px;
            margin-left: auto;
        }
    }
}

.growth-chart {
    margin-bottom: 20px;
}

.user-behavior-chart {
    height: 300px;
}

@media screen and (max-width: 425px) {
    .welcome-img {
        display: none;
    }
}
@media screen and (max-width: 1200px) {
    .lg-mb-20 {
        margin-bottom: 20px;
    }
}

html.dark {
    .welcome {
        background-color: var(--xa-bg-color-overlay);
    }
    .small-panel {
        background-color: var(--xa-bg-color-overlay);
        .small-panel-content {
            color: var(--el-text-color-regular);
        }
    }
    .working {
        .working-opt {
            background-color: rgba($color: #fffefe, $alpha: 0.3);
        }
    }
}
</style>
