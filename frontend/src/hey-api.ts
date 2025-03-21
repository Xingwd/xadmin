import type { CreateClientConfig } from './client/client.gen'
import { Local } from '/@/utils/storage'
import { ACCESS_TOKEN } from '/@/stores/constant/cacheKey'
import { getUrl } from './utils/query'

export const createClientConfig: CreateClientConfig = (config) => ({
    ...config,
    auth: () => Local.get(ACCESS_TOKEN),
    baseURL: getUrl(),
})
