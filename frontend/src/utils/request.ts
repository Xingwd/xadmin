import { ElNotification } from 'element-plus'
import { i18n } from '/@/lang/index'

/**
 * 根据运行环境获取基础请求URL
 */
export const getUrl = (): string => {
    const value: string = import.meta.env.VITE_API_URL as string
    return value == 'getCurrentDomain' ? window.location.protocol + '//' + window.location.host : value
}

/**
 * 根据运行环境获取基础请求URL的端口
 */
export const getUrlPort = (): string => {
    const url = getUrl()
    return new URL(url).port
}

/**
 * 判断是否成功
 * @param {*} status
 */
export const isSuccess = (status: number): boolean => {
    return status >= 200 && status < 300
}

/**
 * 处理状态
 * @param {*} result
 */
export function httpStatusHandle(result: any) {
    let message = '',
        messageType: any = 'error'
    if (result && result.status) {
        switch (result.status) {
            case 200:
                messageType = 'success'
                message = i18n.global.t('axios.Operation successful')
                break
            case 201:
                messageType = 'success'
                message = i18n.global.t('axios.Operation successful')
                break
            case 302:
                message = i18n.global.t('axios.Interface redirected!')
                break
            case 400:
                message = i18n.global.t('axios.Incorrect parameter!')
                break
            case 401:
                message = i18n.global.t('axios.You do not have permission to operate!')
                break
            case 403:
                message = i18n.global.t('axios.You do not have permission to operate!')
                break
            case 404:
                message = i18n.global.t('axios.Error requesting address:') + result.response.config.url
                break
            case 408:
                message = i18n.global.t('axios.Request timed out!')
                break
            case 409:
                message = i18n.global.t('axios.The same data already exists in the system!')
                break
            case 500:
                message = i18n.global.t('axios.Server internal error!')
                break
            case 501:
                message = i18n.global.t('axios.Service not implemented!')
                break
            case 502:
                message = i18n.global.t('axios.Gateway error!')
                break
            case 503:
                message = i18n.global.t('axios.Service unavailable!')
                break
            case 504:
                message = i18n.global.t('axios.The service is temporarily unavailable Please try again later!')
                break
            case 505:
                message = i18n.global.t('axios.HTTP version is not supported!')
                break
            default:
                message = i18n.global.t('axios.Abnormal problem, please contact the website administrator!')
                break
        }
    }
    if (result.message) {
        if (result.message.includes('timeout')) message = i18n.global.t('axios.Network request timeout!')
        if (result.message.includes('Network'))
            message = window.navigator.onLine ? i18n.global.t('axios.Server exception!') : i18n.global.t('axios.You are disconnected!')
    }

    if (message !== '') {
        ElNotification({
            type: messageType,
            message,
            zIndex: 9999,
        })
    }
}
