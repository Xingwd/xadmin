import { test, expect } from '@playwright/test'
import { HomePage } from './pages/home.page'

test.describe('Home Page', () => {
    test.beforeEach(async ({ page }) => {
        const homePage = new HomePage(page)
        await homePage.goto()
    })

    test('should display welcome section', async ({ page }) => {
        const homePage = new HomePage(page)
        await homePage.expectLoaded()

        await expect(homePage.welcomeTitle).toBeVisible()
        await expect(homePage.welcomeNote).toBeVisible()
    })

    test('should display statistics panels', async ({ page }) => {
        const homePage = new HomePage(page)

        // Wait for panels to load
        await expect(homePage.smallPanelBox).toBeVisible()
    })

    test('should display frequently used menus', async ({ page }) => {
        const homePage = new HomePage(page)

        // General panel box should be visible
        await expect(homePage.generalPanelBox).toBeVisible()
    })

    test('should display behavior charts', async ({ page }) => {
        const homePage = new HomePage(page)

        await expect(homePage.behaviorCharts).toHaveCount(2)
    })
})
