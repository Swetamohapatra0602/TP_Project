class myAccount{
    constructor(page){
        this.myAccountHome=page.locator('// a[@href="my-wishlist.php"]/ancestor::div [@class="cnt-account"] /descendant::a[@href="my-account.php"]')
        //after clicking on my Account ,now entering the page and 
        // check the locator for elements
        //YOUR CHECKOUT PROGRESS

        this.myAccountLink=page.locator('//a[text()="Shipping / Billing Address"]/ancestor::div[@class="panel-body"]/descendant::a[text()="My Account"]')
        this.ShippingBillingLink=page.locator('//a[text()="Shipping / Billing Address"]')
        this.OrderHistoryLink=page.locator('//a[text()="Order History"]')
        this.PaymentPendingLink=page.locator('//a[text()="Payment Pending Order"]')
    }
}
export default myAccount
