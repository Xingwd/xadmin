import { test, expect } from '@playwright/test'
import { LoginPage } from './pages/login.page'
import { firstSuperuser, firstSuperuserPassword } from './config.ts'
import { HomePage } from './pages/home.page'

test.describe('Login Page', () => {
    // Login tests should run without auth state
    test.use({ storageState: { cookies: [], origins: [] } })
    test('should display login form', async ({ page }) => {
        const loginPage = new LoginPage(page)
        await loginPage.goto()

        await expect(loginPage.usernameInput).toBeVisible()
        await expect(loginPage.passwordInput).toBeVisible()
        await expect(loginPage.submitButton).toBeVisible()
        await expect(loginPage.submitButton).toContainText('登录')
    })

    test('should login successfully with valid credentials', async ({ page }) => {
        const loginPage = new LoginPage(page)
        await loginPage.goto()
        await loginPage.login(firstSuperuser, firstSuperuserPassword)

        // Should redirect to home page
        const homePage = new HomePage(page)
        await expect(homePage.welcomeTitle).toBeVisible({ timeout: 10000 })
        await expect(page).toHaveURL(/#/)
    })

    test('should show error with invalid credentials', async ({ page }) => {
        const loginPage = new LoginPage(page)
        await loginPage.goto()
        await loginPage.login('admin', 'wrongpassword')

        // Should show error message
        await expect(loginPage.errorMessage).toBeVisible({ timeout: 5000 })
    })

    test('should validate required fields', async ({ page }) => {
        const loginPage = new LoginPage(page)
        await loginPage.goto()

        // Click submit without filling anything
        await loginPage.submitButton.click()

        // Should show validation error on username
        const usernameFormItem = page.locator('.login .el-form-item').first()
        await expect(usernameFormItem.locator('.el-form-item__error')).toBeVisible()
    })
})
