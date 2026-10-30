import testData from "../testData/testData.json";
import productDetails from "./productDetails.page";

class wishlistPersistence {
  constructor(page) {
    this.page = page;
    this.product = new productDetails(page);
    this.wishlistRow = page.locator("table tbody tr").filter({
      has: page.locator(".product-name a").filter({ hasText: this.product.productName }),
    });
    this.productLink = this.wishlistRow.getByRole("link", { name: this.product.productName, exact: true });
    this.wishlistButton = page.locator('a[href*="action=wishlist"]');
    this.removeLink = this.wishlistRow.locator('a[href*="?del="]');
    this.url = "my-wishlist.php";
  }

  async open() {
    await this.page.goto(this.url, { waitUntil: "domcontentloaded" });
  }

  async saveToWishlist() {
    await Promise.all([
      this.page.waitForURL(this.url, { waitUntil: "load" }),
      this.wishlistButton.click(),
    ]);
  }

  async clearWishlist() {
    await this.open();
    if (await this.wishlistRow.count()) {
      await this.removeLink.click();
    }
    await this.page.reload();
  }
}

export default wishlistPersistence;
