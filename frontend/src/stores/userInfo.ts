import { defineStore } from 'pinia'
import { USER_INFO } from '/@/stores/constant/cacheKey'
import type { UserMePublic } from '/@/client/types.gen'

export const useUserInfo = defineStore('userInfo', {
    state: (): UserMePublic => {
        return {
            username: '',
            is_active: true,
            is_superuser: false,
            full_name: '',
            id: 0,
            last_login_at: '',
            created_at: '',
            updated_at: '',
        }
    },
    actions: {
        dataFill(state: UserMePublic) {
            this.$state = { ...this.$state, ...state }
        },
    },
    persist: {
        key: USER_INFO,
    },
})
