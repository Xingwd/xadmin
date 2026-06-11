import { test, expect } from '@playwright/test'
import { UserInfoPage } from './pages/userInfo.page'

test.describe('User Info', () => {
    test.beforeEach(async ({ page }) => {
        const userInfoPage = new UserInfoPage(page)
        await userInfoPage.goto()
    })

    test('should display user info form', async ({ page }) => {
        const userInfoPage = new UserInfoPage(page)
        // User avatar and info should be visible
        await expect(userInfoPage.userInfo).toBeVisible()
        await expect(userInfoPage.avatar).toBeVisible()

        // Form fields should be visible
        await expect(userInfoPage.userInfoForm).toBeVisible()
    })

    test('should display operation log timeline', async ({ page }) => {
        const userInfoPage = new UserInfoPage(page)
        // Operation log card should be visible
        await expect(userInfoPage.operationLogCard).toBeVisible()

        // Timeline should be visible if there are logs
        const timelineItems = userInfoPage.timelineItems
        const count = await timelineItems.count()
        if (count > 0) {
            await expect(timelineItems.first()).toBeVisible()
        }
    })

    test('should have pagination for operation logs', async ({ page }) => {
        const userInfoPage = new UserInfoPage(page)
        await expect(userInfoPage.pagination).toBeVisible()
    })
})
