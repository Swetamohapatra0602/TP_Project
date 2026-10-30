class Furniture{
    constructor (page){

        this.FurnitureCategory=page.locator( '//a[text()=" Furniture"]')
        this.addToCart=page.locator('//a[text()="Induscraft Solid Wood King Bed With Storage"]/ancestor::div[@class="product"]/descendant::button[text()="Add to cart"]')
        
    }
}
export default Furniture
