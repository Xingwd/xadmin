import { Page, Locator, expect } from '@playwright/test'

export class RulePage {
    readonly page: Page
    readonly addButton: Locator
    readonly editButton: Locator
    readonly deleteButton: Locator
    readonly refreshButton: Locator
    readonly unfoldButton: Locator
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
        this.unfoldButton = page
            .locator('.table-header .el-button--warning.table-header-operate, .table-header .el-button--danger.table-header-operate')
            .filter({ hasText: /展开|收缩/ })
        this.dialog = page.locator('.xa-operate-dialog')
        this.dialogTitle = page.locator('.xa-operate-dialog .title')
        this.saveButton = page.locator('.xa-operate-dialog .el-dialog__footer .el-button--primary')
        this.cancelButton = page.locator('.xa-operate-dialog .el-dialog__footer .el-button:not(.el-button--primary)')
        this.table = page.locator('.xa-data-table')
        this.tableRows = page.locator('.xa-data-table .el-table__row')
    }

    async goto() {
        await this.page.goto('/#/system/rules')
        await expect(this.table).toBeVisible()
    }

    async addRule(title: string, name: string) {
        await this.addButton.click()
        await expect(this.dialog).toBeVisible()
        await expect(this.dialogTitle).toContainText('添加')

        const form = this.dialog.locator('.xa-Add-form')
        await form.locator('.el-form-item').nth(1).locator('input').fill(title)
        await form.locator('.el-form-item').nth(2).locator('input').fill(name)

        await this.saveButton.click()
    }

    async deleteFirstRule() {
        await this.tableRows.first().click()
        await this.deleteButton.click()
        await this.page.locator('.el-popconfirm__action .el-button--danger').click()
    }

    async toggleUnfold() {
        await this.unfoldButton.click()
    }
}
