import { useMutation } from '@pinia/colada'
import router from '/@/router'
import { BodyLoginAccessToken, loginAccessToken, loginTestToken } from '/@/client'
import { Local } from '/@/utils/storage'
import { ACCESS_TOKEN } from '/@/stores/constant/cacheKey'

const isLoggedIn = () => {
    if (Local.get(ACCESS_TOKEN) !== null) {
        loginTestToken().then((res) => {
            if (res.status !== 200) {
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
