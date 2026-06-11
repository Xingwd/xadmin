import { Page, Locator, expect } from '@playwright/test'

export class OperationLogPage {
    readonly page: Page
    readonly deleteButton: Locator
    readonly refreshButton: Locator
    readonly dialog: Locator
    readonly dialogTitle: Locator
    readonly table: Locator
    readonly tableRows: Locator
    readonly infoButton: Locator

    constructor(page: Page) {
        this.page = page
        this.refreshButton = page.locator('.table-header .el-button--info.table-header-operate')
        this.deleteButton = page.locator('.table-header .el-button--danger.table-header-operate')
        this.dialog = page.locator('.xa-operate-dialog')
        this.dialogTitle = page.locator('.xa-operate-dialog .title')
        this.table = page.locator('.xa-data-table')
        this.tableRows = page.locator('.xa-data-table .el-table__row')
        this.infoButton = page.locator('.table-row-edit')
    }

    async goto() {
        await this.page.goto('/#/system/operation-logs')
        await expect(this.table).toBeVisible()
    }

    async viewInfo() {
        await this.tableRows.first().locator('.table-row-edit').click()
        await expect(this.dialog).toBeVisible()
        await expect(this.dialogTitle).toContainText('查看详情')
    }

    async deleteFirstLog() {
        await this.tableRows.first().click()
        await this.deleteButton.click()
        await this.page.locator('.el-popconfirm__action .el-button--danger').click()
    }
}
