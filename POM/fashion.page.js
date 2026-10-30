class   Fashion{
    constructor (page){

        this.FashionCategory=page.locator( '//a[text()=" Fashion"]')
        this.addToCart=page.locator('//a[text()="Asian Casuals  (White, White)"]/ancestor::div[@class="product"]/descendant::button[text()="Add to cart"]')
        
    }
}
export default Fashion
