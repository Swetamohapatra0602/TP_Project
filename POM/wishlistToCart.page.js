import wishlistPersistence from "./wishlistPersistence.page";
import repeatedAddToCart from "./repeatedAddToCart.page";

class wishlistToCart {
  constructor(page) {
    this.wishlist = new wishlistPersistence(page);
    this.cart = new repeatedAddToCart(page);
    this.price = this.wishlist.wishlistRow.locator(".price");
    this.addToCart = this.wishlist.wishlistRow.getByRole("link", { name: "Add to cart", exact: true });
  }

  async addSavedProduct() {
    await this.addToCart.click();
    await this.cart.open();
  }
}

export default wishlistToCart;
