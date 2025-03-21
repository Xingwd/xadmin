<template>
    <el-header v-if="!navTabs.state.tabFullScreen" class="layout-header">
        <component :is="config.layout.layoutMode + 'NavBar'"></component>
    </el-header>
</template>
<script setup lang="ts">
import { useConfig } from '/@/stores/config'
import { useNavTabs } from '/@/stores/navTabs'
import DefaultNavBar from '/@/layouts/components/navBar/default.vue'
import ClassicNavBar from '/@/layouts/components/navBar/classic.vue'
import StreamlineNavBar from '/@/layouts/components/menus/menuHorizontal.vue'
import DoubleNavBar from '/@/layouts/components/navBar/double.vue'

defineOptions({
    name: 'layout/header',
    components: { DefaultNavBar, ClassicNavBar, StreamlineNavBar, DoubleNavBar },
})

const config = useConfig()
const navTabs = useNavTabs()
</script>

<style scoped lang="scss">
.layout-header {
    height: auto;
    padding: 0;
}
</style>
