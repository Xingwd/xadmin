<template>
    <component :is="config.layout.layoutMode"></component>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useConfig } from '/@/stores/config'
import { useNavTabs } from '/@/stores/navTabs'
import { useSiteConfig } from '/@/stores/siteConfig'
import { useUserInfo } from '/@/stores/userInfo'
import { useRoute } from 'vue-router'
import Default from '/@/layouts/container/default.vue'
import Classic from '/@/layouts/container/classic.vue'
import Streamline from '/@/layouts/container/streamline.vue'
import Double from '/@/layouts/container/double.vue'
import { onMounted, onBeforeMount } from 'vue'
import { Session } from '/@/utils/storage'
import { handleRoute, getFirstRoute, routePush } from '/@/utils/router'
import router from '/@/router/index'
import { useEventListener } from '@vueuse/core'
import { BEFORE_RESIZE_LAYOUT } from '/@/stores/constant/cacheKey'
import { isEmpty } from 'lodash-es'
import { setNavTabsWidth } from '/@/utils/layout'
import { isLoggedIn } from '/@/utils/useAuth'
import { usersReadUserMe } from '/@/client'

defineOptions({
    components: { Default, Classic, Streamline, Double },
})

const navTabs = useNavTabs()
const config = useConfig()
const route = useRoute()
const siteConfig = useSiteConfig()
const userInfo = useUserInfo()

const state = reactive({
    autoMenuCollapseLock: false,
})

onMounted(async () => {
    if (!(await isLoggedIn())) return router.push({ name: 'login' })
    init()
    setNavTabsWidth()
    useEventListener(window, 'resize', setNavTabsWidth)
})
onBeforeMount(() => {
    onAdaptiveLayout()
    useEventListener(window, 'resize', onAdaptiveLayout)
})

const init = () => {
    siteConfig.dataFill({
        siteName: import.meta.env.VITE_SITE_NAME,
        userInitialize: false,
    })
    /**
     * 后台初始化请求，动态路由等信息
     */
    usersReadUserMe().then((res) => {
        if (res.data) {
            userInfo.dataFill(res.data)
            siteConfig.setUserInitialize(true)

            if (res.data?.rules) {
                handleRoute(res.data.rules)

                // 预跳转到上次路径
                if (route.params.to) {
                    const lastRoute = JSON.parse(route.params.to as string)
                    if (lastRoute.path != '/') {
                        let query = !isEmpty(lastRoute.query) ? lastRoute.query : {}
                        routePush({ path: lastRoute.path, query: query })
                        return
                    }
                }

                // 跳转到第一个菜单
                let firstRoute = getFirstRoute(navTabs.state.tabsViewRoutes)
                if (firstRoute) routePush(firstRoute.path)
            }
        } else if (res.status == 401) {
            router.push({ path: '/401' })
        }
    })
}

const onAdaptiveLayout = () => {
    let defaultBeforeResizeLayout = {
        layoutMode: config.layout.layoutMode,
        menuCollapse: config.layout.menuCollapse,
    }
    let beforeResizeLayout = Session.get(BEFORE_RESIZE_LAYOUT)
    if (!beforeResizeLayout) Session.set(BEFORE_RESIZE_LAYOUT, defaultBeforeResizeLayout)

    const clientWidth = document.body.clientWidth
    if (clientWidth < 1024) {
        /**
         * 锁定窗口改变自动调整 menuCollapse
         * 避免已是小窗且打开了菜单栏时，意外的自动关闭菜单栏
         */
        if (!state.autoMenuCollapseLock) {
            state.autoMenuCollapseLock = true
            config.setLayout('menuCollapse', true)
        }
        config.setLayout('shrink', true)
        config.setLayoutMode('Classic')
    } else {
        state.autoMenuCollapseLock = false
        let beforeResizeLayoutTemp = beforeResizeLayout || defaultBeforeResizeLayout

        config.setLayout('menuCollapse', beforeResizeLayoutTemp.menuCollapse)
        config.setLayout('shrink', false)
        config.setLayoutMode(beforeResizeLayoutTemp.layoutMode)
    }
}
</script>
