import { Page, Locator, expect } from '@playwright/test'

export class HomePage {
    readonly page: Page
    readonly welcomeTitle: Locator
    readonly welcomeNote: Locator
    readonly generalPanelBox: Locator
    readonly smallPanelBox: Locator
    readonly behaviorCharts: Locator
    readonly navTabs: Locator
    readonly asideMenu: Locator

    constructor(page: Page) {
        this.page = page
        this.welcomeTitle = page.locator('.welcome-title')
        this.welcomeNote = page.locator('.welcome-note')
        this.generalPanelBox = page.locator('.general-panel-box')
        this.smallPanelBox = page.locator('.small-panel-box')
        this.behaviorCharts = page.locator('.user-behavior-chart')
        this.navTabs = page.locator('.xa-nav-tab')
        this.asideMenu = page.locator('.el-menu')
    }

    async goto() {
        await this.page.goto('/#/home')
    }

    async expectLoaded() {
        await expect(this.welcomeTitle).toBeVisible()
        await expect(this.smallPanelBox).toBeVisible()
    }

    async navigateToMenu(menuText: string) {
        const menuItem = this.page.locator('.el-menu-item, .el-sub-menu__title').filter({ hasText: menuText })
        await menuItem.click()
    }
}
