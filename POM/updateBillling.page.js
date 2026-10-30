class updateBilling{
    constructor (page){
        this.billingaddresslink=page.locator('//a[@href="#collapseOne"]')
        this.billingaddressTF=page.locator('//textarea[@name="billingaddress"]')
        this.bilingstateTF=page.locator('//input[@id="bilingstate"]')
        this.billingcityTF=page.locator('//input[@id="billingcity"]')
        this.billingpincodeTF=page.locator('//input[@id="billingpincode"]')
        this.updateButton=page.locator('//button[@name="update"]')
        
    }
}
export default updateBilling
