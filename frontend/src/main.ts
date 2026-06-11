import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { loadLang } from '/@/lang/index'
import { registerIcons } from '/@/utils/common'
import ElementPlus from 'element-plus'
import mitt from 'mitt'
import pinia from '/@/stores/index'
import { PiniaColada } from '@pinia/colada'
import { directives } from '/@/utils/directives'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/display.css'
import 'font-awesome/css/font-awesome.min.css'
import '/@/styles/index.scss'
import { getUrl } from './utils/request.ts'
import { OpenAPI } from './client/index.ts'
import { Local } from './utils/storage.ts'
import { ACCESS_TOKEN } from './stores/constant/cacheKey.ts'
// modules import mark, Please do not remove.

OpenAPI.BASE = getUrl()
OpenAPI.TOKEN = async () => {
    return Local.get(ACCESS_TOKEN) || ''
}

OpenAPI.interceptors.response.use((response) => {
    if (response.status === 401) {
        Local.remove(ACCESS_TOKEN)
        router.push({ name: 'login' })
    } else if (response.status === 403) {
        router.push({ name: 'noPower' })
    }
    return response
})

async function start() {
    const app = createApp(App)
    app.use(pinia)
    app.use(PiniaColada)

    // 全局语言包加载
    await loadLang(app)

    app.use(router)
    app.use(ElementPlus)

    // 全局注册
    directives(app) // 指令
    registerIcons(app) // icons

    app.mount('#app')

    // modules start mark, Please do not remove.

    app.config.globalProperties.eventBus = mitt()
}
start()
