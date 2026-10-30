class Book{
    constructor (page){

        this.bookCategory=page.locator( '//a[text()=" Books"]')
        this.addToCart=page.locator('//a[text()="The Wimpy Kid Do -It- Yourself Book"]/ancestor::div[@class="product"]/descendant::button[text()="Add to cart"]')
        
    }
}
export default Book
