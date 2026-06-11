import { test, expect } from '@playwright/test'
import { OperationLogPage } from './pages/operationLog.page'

test.describe('Operation Log', () => {
    test.beforeEach(async ({ page }) => {
        const logPage = new OperationLogPage(page)
        await logPage.goto()
    })

    test('should display operation log table', async ({ page }) => {
        const logPage = new OperationLogPage(page)

        await expect(logPage.table).toBeVisible()
        await expect(logPage.refreshButton).toBeVisible()
    })

    test('should view log details', async ({ page }) => {
        const logPage = new OperationLogPage(page)

        await logPage.viewInfo()
        await expect(logPage.dialog).toBeVisible()
        await expect(page.locator('.xa-operate-dialog')).toContainText('请求方法')
    })

    test('should refresh log table', async ({ page }) => {
        const logPage = new OperationLogPage(page)

        await logPage.refreshButton.click()
        await expect(logPage.table).toBeVisible()
    })
})
