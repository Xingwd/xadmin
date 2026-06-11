import { test as setup } from '@playwright/test'
import { firstSuperuser, firstSuperuserPassword } from './config.ts'
import { LoginPage } from './pages/login.page'
import { HomePage } from './pages/home.page'

const authFile = 'playwright/.auth/user.json'

setup('authenticate', async ({ page }) => {
    const loginPage = new LoginPage(page)
    await loginPage.goto()

    // Fill credentials
    await loginPage.login(firstSuperuser, firstSuperuserPassword)

    // Wait for redirect to home page
    const homePage = new HomePage(page)
    await homePage.expectLoaded()

    // Save auth state
    await page.context().storageState({ path: authFile })
})
