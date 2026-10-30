class   Electronics{
    constructor (page){

        this.ElectronicsCategory=page.locator('//a[text()=" Electronics"]')
        this.addToCart=page.locator('//a[text()="Micromax 81cm (32) HD Ready LED TV  (32T6175MHD, 2 x HDMI, 2 x USB)"]/ancestor::div[@class="product"]/descendant::button[text()="Add to cart"]')
        
    }
}
export default Electronics
