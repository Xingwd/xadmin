import { test, expect } from '@playwright/test'
import { UserPage } from './pages/user.page'

test.describe('User Management', () => {
    test.beforeEach(async ({ page }) => {
        const userPage = new UserPage(page)
        await userPage.goto()
    })

    test('should display user table', async ({ page }) => {
        const userPage = new UserPage(page)

        await expect(userPage.table).toBeVisible()
        await expect(userPage.addButton).toBeVisible()
    })

    test('should add a new user', async ({ page }) => {
        const userPage = new UserPage(page)
        const testUsername = `testuser_${Date.now()}`

        await userPage.addUser({
            username: testUsername,
            password: 'Test123!',
            fullName: 'Test User',
        })

        // Wait for dialog to close
        await expect(userPage.dialog).not.toBeVisible()

        // Verify user appears in table
        await userPage.search(testUsername)
        await expect(page.locator('.xa-data-table')).toContainText(testUsername)
    })

    test('should search users', async ({ page }) => {
        const userPage = new UserPage(page)

        await userPage.search('admin')
        await expect(page.locator('.xa-data-table')).toContainText('admin')
    })

    test('should refresh user table', async ({ page }) => {
        const userPage = new UserPage(page)

        await userPage.refreshButton.click()
        await expect(userPage.table).toBeVisible()
    })
})
