import testData from "../testData/testData.json";
import productDetails from "./productDetails.page";

class repeatedAddToCart {
  constructor(page) {
    this.page = page;
    this.product = new productDetails(page);
    this.cartRow = page.locator('form[name="cart"] tbody tr').filter({ has: this.product.productLink });
    this.quantities = page.locator('input[name^="quantity["]');
    this.quantity = this.cartRow.locator('input[name^="quantity["]');
    this.priceCells = this.cartRow.locator(".cart-product-sub-total");
    this.rowTotal = this.cartRow.locator(".cart-product-grand-total");
    this.grandTotal = page.locator(".cart-grand-total span");
    this.productLink = this.cartRow.getByRole("link", { name: this.product.productName, exact: true });
    this.emptyCart = page.getByText("Your shopping Cart is empty", { exact: true });
    this.removeCheckbox = this.cartRow.locator('input[name="remove_code[]"]');
    this.updateButton = page.getByRole("button", { name: "Update shopping cart", exact: true });
    // Required address fields share the cart form and must be filled for removal.
    this.addressFields = Object.entries({
      billingaddress: "Test address", bilingstate: "KT", billingcity: "Bangalore", billingpincode: "560001",
      shippingaddress: "Test address", shippingstate: "KT", shippingcity: "Bangalore", shippingpincode: "560001",
    }).map(([name, value]) => ({ field: page.locator(`[name="${name}"]`), value }));
  }

  async open() {
    await this.page.goto("my-cart.php", { waitUntil: "domcontentloaded" });
  }

  async addBook() {
    await this.product.openBooks();
    await this.product.addToCart.click();
    await this.open();
  }

  async clearCart() {
    await this.open();
    if (await this.cartRow.count()) {
      for (const { field, value } of this.addressFields) {
        await field.fill(value);
      }
      await this.removeCheckbox.check();
      await this.updateButton.click();
    }
  }
}

export default repeatedAddToCart;
