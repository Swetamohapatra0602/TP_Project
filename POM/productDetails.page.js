import testData from "../testData/testData.json";

class productDetails {
  constructor(page) {
    this.page = page;
    this.productName = testData.paymentPending.productName;
    this.productLink = page.getByRole("link", { name: this.productName, exact: true });
    this.productHeading = page.locator("h1");
    this.addToCart = page.locator(".product").filter({ has: this.productLink })
      .getByRole("button", { name: "Add to cart", exact: true });
  }

  async openBooks() {
    await this.page.goto("category.php?cid=3", { waitUntil: "domcontentloaded" });
  }

  async open() {
    await this.openBooks();
    await this.productLink.click();
  }
}

export default productDetails;
