import { useMutation } from '@pinia/colada'
import router from '/@/router'
import { BodyLoginAccessToken, loginAccessToken, loginTestToken } from '/@/client'
import { Local } from '/@/utils/storage'
import { ACCESS_TOKEN } from '/@/stores/constant/cacheKey'
import { isSuccess } from '/@/utils/request'

const isLoggedIn = async () => {
    if (Local.get(ACCESS_TOKEN) !== null) {
        await loginTestToken().then((res) => {
            const status = res.status
            if (status && typeof status === 'number' && !isSuccess(status)) {
                Local.remove(ACCESS_TOKEN)
            }
        })
    }
    return Local.get(ACCESS_TOKEN) !== null
}

const useAuth = () => {
    const login = async (data: BodyLoginAccessToken) => {
        const res = await loginAccessToken({ body: data })
        if (res.data) {
            Local.set(ACCESS_TOKEN, res.data.access_token)
        }
    }

    const loginMutation = useMutation({
        mutation: login,
        onSuccess: () => {
            router.push({ name: '/' })
        },
        onError: (error) => {
            console.log(error)
        },
    })

    const logout = () => {
        Local.remove(ACCESS_TOKEN)
        router.push({ name: 'login' })
    }

    return {
        loginMutation,
        logout,
    }
}

export { isLoggedIn }
export default useAuth
