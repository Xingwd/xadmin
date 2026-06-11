import { test, expect } from '@playwright/test'
import { RulePage } from './pages/rule.page'

test.describe('Rule Management', () => {
    test.beforeEach(async ({ page }) => {
        const rulePage = new RulePage(page)
        await rulePage.goto()
    })

    test('should display rule table', async ({ page }) => {
        const rulePage = new RulePage(page)

        await expect(rulePage.table).toBeVisible()
        await expect(rulePage.addButton).toBeVisible()
    })

    test('should expand and shrink all rules', async ({ page }) => {
        const rulePage = new RulePage(page)

        // Click expand all
        await rulePage.unfoldButton.click()
        await expect(rulePage.table).toBeVisible()

        // Click shrink all
        await rulePage.unfoldButton.click()
        await expect(rulePage.table).toBeVisible()
    })

    test('should refresh rule table', async ({ page }) => {
        const rulePage = new RulePage(page)

        await rulePage.refreshButton.click()
        await expect(rulePage.table).toBeVisible()
    })
})
