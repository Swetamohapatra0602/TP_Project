class signin{
    constructor (page){
        this.email=page.locator('//input[@id="exampleInputEmail1"]')
        this.password=page.locator('//input[@id="exampleInputPassword1"]')
        this.loginButton=page.locator('//button[@name="login"]')
    }
}
export default signin
