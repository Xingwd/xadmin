<template>
    <div class="layouts-menu-horizontal">
        <div class="menu-horizontal-logo" v-if="config.layout.menuShowTopBar">
            <Logo />
        </div>
        <el-scrollbar ref="layoutMenuScrollbarRef" class="horizontal-menus-scrollbar">
            <el-menu ref="layoutMenuRef" class="menu-horizontal" mode="horizontal" :default-active="state.defaultActive">
                <MenuTree :extends="{ position: 'horizontal', level: 1 }" :menus="navTabs.state.tabsViewRoutes" />
            </el-menu>
        </el-scrollbar>
        <NavMenus />
    </div>
</template>

<script setup lang="ts">
import { nextTick, onMounted, reactive } from 'vue'
import Logo from '/@/layouts/components/logo.vue'
import MenuTree from '/@/layouts/components/menus/menuTree.vue'
import { useRoute, onBeforeRouteUpdate, type RouteLocationNormalizedLoaded } from 'vue-router'
import { useConfig } from '/@/stores/config'
import { useNavTabs } from '/@/stores/navTabs'
import NavMenus from '/@/layouts/components/navMenus.vue'
import { layoutMenuRef, layoutMenuScrollbarRef } from '/@/stores/refs'
import horizontalScroll from '/@/utils/horizontalScroll'

const config = useConfig()
const navTabs = useNavTabs()
const route = useRoute()

const state = reactive({
    defaultActive: '',
})

/**
 * 激活当前路由对应的菜单
 */
const currentRouteActive = (currentRoute: RouteLocationNormalizedLoaded) => {
    const tabView = navTabs.getTabsViewDataByRoute(currentRoute)
    if (tabView) {
        // 以路由 fullPath 匹配的菜单优先，且 fullPath 无匹配时，回退到 path 的匹配菜单
        state.defaultActive = tabView.meta!.matched as string
    }
}

// 滚动条滚动到激活菜单所在位置
const verticalMenusScroll = () => {
    nextTick(() => {
        let activeMenu: HTMLElement | null = document.querySelector('.el-menu.menu-horizontal li.is-active')
        if (!activeMenu) return false
        layoutMenuScrollbarRef.value?.setScrollTop(activeMenu.offsetTop)
    })
}

onMounted(() => {
    currentRouteActive(route)
    verticalMenusScroll()

    new horizontalScroll(layoutMenuScrollbarRef.value!.wrapRef!)
})

onBeforeRouteUpdate((to) => {
    currentRouteActive(to)
})
</script>

<style scoped lang="scss">
.layouts-menu-horizontal {
    display: flex;
    align-items: center;
    width: 100vw;
    height: var(--el-header-height);
    background-color: var(--xa-bg-color-overlay);
    border-bottom: 1px solid var(--el-color-info-light-8);
}
.menu-horizontal-logo {
    width: 180px;
    &:hover {
        background-color: v-bind('config.getColorVal("headerBarHoverBackground")');
    }
}
.horizontal-menus-scrollbar {
    flex: 1;
    height: var(--el-header-height);
}
.menu-horizontal {
    border: none;
    --el-menu-bg-color: v-bind('config.getColorVal("menuBackground")');
    --el-menu-text-color: v-bind('config.getColorVal("menuColor")');
    --el-menu-active-color: v-bind('config.getColorVal("menuActiveColor")');
}

.el-sub-menu .icon,
.el-menu-item .icon {
    vertical-align: middle;
    margin-right: 5px;
    width: 24px;
    text-align: center;
    flex-shrink: 0;
}
.is-active .icon {
    color: var(--el-menu-active-color) !important;
}
.el-menu-item.is-active {
    background-color: v-bind('config.getColorVal("menuActiveBackground")');
}
</style>
