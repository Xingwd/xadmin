import { Page, Locator, expect } from '@playwright/test'

export class LoginPage {
    readonly page: Page
    readonly usernameInput: Locator
    readonly passwordInput: Locator
    readonly submitButton: Locator
    readonly loginBox: Locator
    readonly languageSwitcher: Locator
    readonly errorMessage: Locator

    constructor(page: Page) {
        this.page = page
        this.usernameInput = page.locator('.login-box input[type="text"]')
        this.passwordInput = page.locator('.login-box input[type="password"]')
        this.submitButton = page.locator('.submit-button')
        this.loginBox = page.locator('.login-box')
        this.languageSwitcher = page.locator('.switch-language .el-dropdown')
        this.errorMessage = page.locator('.el-message--error')
    }

    async goto() {
        await this.page.goto('/#/login')
        // Wait for login page to be ready
        await expect(this.loginBox).toBeVisible()
    }

    async login(username: string, password: string) {
        // Fill credentials
        await this.usernameInput.fill(username)
        await this.passwordInput.fill(password)
        // Click login button
        await this.submitButton.click()
    }

    async expectErrorMessage() {
        await expect(this.errorMessage).toBeVisible()
    }
}
