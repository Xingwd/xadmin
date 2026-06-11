import { Page, Locator, expect } from '@playwright/test'

export class UserInfoPage {
    readonly page: Page
    readonly userInfo: Locator
    readonly avatar: Locator
    readonly userInfoForm: Locator
    readonly operationLogCard: Locator
    readonly timelineItems: Locator
    readonly pagination: Locator

    constructor(page: Page) {
        this.page = page
        this.userInfo = page.locator('.user-info')
        this.avatar = page.locator('.avatar')
        this.userInfoForm = page.locator('.user-info-form')
        this.operationLogCard = page.locator('.el-card')
        this.timelineItems = page.locator('.el-timeline-item')
        this.pagination = page.locator('.el-pagination')
    }

    async goto() {
        await this.page.goto('/#/routine/user-info')
        await expect(this.userInfo).toBeVisible()
    }
}
