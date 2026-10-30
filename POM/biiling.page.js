class billing{
    constructor (page){
        this.shippingaddress=page.locator('//textarea[@name="shippingaddress"]')
        this.shippingstate=page.locator('//input[@name="shippingstate"]')
        this.shippingcity=page.locator('//input[@name="shippingcity"]')
        
        this.shippingpincode=page.locator('//input[@name="shippingpincode"]')
        this.updateButton=page.locator('//button[@name="shipupdate"]')
        
    }
}
export default billing
