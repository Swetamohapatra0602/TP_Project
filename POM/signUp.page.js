class signUp{
    constructor (page){
        this.fullName=page.locator('//input[@id="fullname"]')
        this.email=page.locator('//input[@id="email"]')
        this.contactno=page.locator('//input[@id="contactno"]')
        this.password=page.locator('//input[@id="password"]')
        this.confirmpassword=page.locator('//input[@id="confirmpassword"]')
        this.submitButton=page.locator('//button[@id="submit"]')

    }
}
export default signUp
