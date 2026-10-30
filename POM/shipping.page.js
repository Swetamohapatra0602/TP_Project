class shipping{
    constructor (page){
        this.billingaddress=page.locator('//textarea[@name="billingaddress"]')
        this.bilingstate=page.locator('//input[@name="bilingstate"]')
        this.billingcity=page.locator('//input[@name="billingcity"]')
        
        this.billingpincode=page.locator('//input[@name="billingpincode"]')
        this.updateButton=page.locator('//button[@name="update"]')
        
    }
}
export default shipping
