import { test, expect } from '@playwright/test'
import { RolePage } from './pages/role.page'

test.describe('Role Management', () => {
    test.beforeEach(async ({ page }) => {
        const rolePage = new RolePage(page)
        await rolePage.goto()
    })

    test('should display role table', async ({ page }) => {
        const rolePage = new RolePage(page)

        await expect(rolePage.table).toBeVisible()
        await expect(rolePage.addButton).toBeVisible()
    })

    test('should add a new role', async ({ page }) => {
        const rolePage = new RolePage(page)
        const testRoleName = `TestRole_${Date.now()}`

        await rolePage.addRole(testRoleName)

        // Wait for dialog to close
        await expect(rolePage.dialog).not.toBeVisible()

        // Verify role appears in table
        await rolePage.search(testRoleName)
        await expect(page.locator('.xa-data-table')).toContainText(testRoleName)
    })

    test('should search roles', async ({ page }) => {
        const rolePage = new RolePage(page)

        await rolePage.search('admin')
        await expect(page.locator('.xa-data-table')).toBeVisible()
    })
})
