import { Page, Locator, expect } from '@playwright/test'

export class UserPage {
    readonly page: Page
    readonly addButton: Locator
    readonly editButton: Locator
    readonly deleteButton: Locator
    readonly refreshButton: Locator
    readonly quickSearchInput: Locator
    readonly dialog: Locator
    readonly dialogTitle: Locator
    readonly saveButton: Locator
    readonly cancelButton: Locator
    readonly table: Locator
    readonly tableRows: Locator

    constructor(page: Page) {
        this.page = page
        this.refreshButton = page.locator('.table-header .el-button--info.table-header-operate')
        this.addButton = page.locator('.table-header .el-button--primary.table-header-operate').first()
        this.editButton = page.locator('.table-header .el-button--primary.table-header-operate').nth(1)
        this.deleteButton = page.locator('.table-header .el-button--danger.table-header-operate')
        this.quickSearchInput = page.locator('.quick-search input')
        this.dialog = page.locator('.xa-operate-dialog')
        this.dialogTitle = page.locator('.xa-operate-dialog .title')
        this.saveButton = page.locator('.xa-operate-dialog .el-dialog__footer .el-button--primary')
        this.cancelButton = page.locator('.xa-operate-dialog .el-dialog__footer .el-button:not(.el-button--primary)')
        this.table = page.locator('.xa-data-table')
        this.tableRows = page.locator('.xa-data-table .el-table__row')
    }

    async goto() {
        await this.page.goto('/#/system/users')
        await expect(this.table).toBeVisible()
    }

    async addUser(data: { username: string; password: string; fullName: string }) {
        await this.addButton.click()
        await expect(this.dialog).toBeVisible()
        await expect(this.dialogTitle).toContainText('添加')

        const form = this.dialog.locator('.xa-Add-form')
        await form.locator('.el-form-item').nth(0).locator('input').fill(data.username)
        await form.locator('.el-form-item').nth(1).locator('input').fill(data.password)
        await form.locator('.el-form-item').nth(2).locator('input').fill(data.fullName)

        await this.saveButton.click()
    }

    async editFirstUser(fullName: string) {
        await this.tableRows.first().locator('.table-row-edit').click()
        await expect(this.dialog).toBeVisible()
        await expect(this.dialogTitle).toContainText('编辑')

        const form = this.dialog.locator('.xa-Edit-form')
        const fullNameInput = form.locator('.el-form-item').nth(2).locator('input')
        await fullNameInput.fill('')
        await fullNameInput.fill(fullName)

        await this.saveButton.click()
    }

    async deleteFirstUser() {
        await this.tableRows.first().click()
        await this.deleteButton.click()
        await this.page.locator('.el-popconfirm__action .el-button--danger').click()
    }

    async search(query: string) {
        await this.quickSearchInput.fill(query)
        await this.page.waitForTimeout(900)
    }
}
