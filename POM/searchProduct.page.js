class searchProduct {
  constructor(page, productName) {
    this.page = page;
    this.searchInput = page.getByPlaceholder("Search here...");
    this.searchButton = page.locator('form[name="search"] button[name="search"]');
    this.productLink = page.locator(".product").getByRole("link", {
      name: productName,
      exact: true,
    });
    this.productHeading = page.locator("h1");
  }

  async open(path) {
    await this.page.goto(path);
  }

  async search(keyword) {
    await this.searchInput.fill(keyword);
    await this.searchButton.click();
  }

  async openProduct() {
    await this.productLink.click();
  }
}

export default searchProduct;
