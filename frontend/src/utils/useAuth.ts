import { useMutation, useQuery } from '@pinia/colada'
import { ElMessage } from 'element-plus'
import router from '/@/router'
import { LoginAccessTokenData, LoginService, UsersService } from '/@/client'
import { Local } from '/@/utils/storage'
import { ACCESS_TOKEN } from '/@/stores/constant/cacheKey'
import { useNavTabs } from '/@/stores/navTabs'

const isLoggedIn = () => {
    return Local.get(ACCESS_TOKEN) !== null
}

const useAuth = () => {
    const { data: user, error: userQueryError } = useQuery({
        key: ['users', 'me'],
        query: () => UsersService.readUserMe(),
        enabled: isLoggedIn(),
    })

    const login = async (data: LoginAccessTokenData) => {
        const res = await LoginService.accessToken(data)
        Local.set(ACCESS_TOKEN, res.access_token)
    }

    const loginMutation = useMutation({
        mutation: login,
        onSuccess: () => {
            useNavTabs().closeAllTab()
            router.push({ name: '/' })
        },
        onError: (error: any) => {
            const msg = error.body?.detail || error.message || 'Login failed'
            ElMessage.error(msg)
        },
    })

    const logout = () => {
        useNavTabs().closeAllTab()
        Local.remove(ACCESS_TOKEN)
        router.push({ name: 'login' })
    }

    return {
        loginMutation,
        logout,
        user,
        userQueryError,
    }
}

export { isLoggedIn }
export default useAuth
