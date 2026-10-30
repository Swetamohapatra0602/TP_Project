class payment{
    constructor (page){
        this.internetBankingRadio=page.locator('//input[@value="Internet Banking"]')
        this.submitButton=page.locator('//input[@value="submit"]')
        
    }
}
export default payment
