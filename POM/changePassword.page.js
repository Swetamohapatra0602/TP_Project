class changePassword{
    constructor(page){
        this.changePWlink=page.locator('//a[@href="#collapseTwo"]')
        this.currentPwTF=page.locator('//input[@id="cpass"]')
         this.newPwTF=page.locator('//input[@id="newpass"]')
          this.confirmPwTF=page.locator('//input[@id="cnfpass"]')
          this.changeButton=page.locator('//button[text()="Change "]')
    }
}
export default changePassword
