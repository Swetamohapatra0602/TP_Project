import productDetails from "./productDetails.page";

class productReview {
  constructor(page) {
    this.page = page;
    this.product = new productDetails(page);
    this.tabs = page.locator(".product-tabs");
    this.reviewTab = this.tabs.locator('a[href="#review"]');
    this.form = page.locator('form[name="review"]');
    this.ratings = ["quality", "price", "value"].map(group =>
      this.form.locator(`input[name="${group}"][value="4"]`));
    this.name = this.form.locator('[name="name"]');
    this.summary = this.form.locator('[name="summary"]');
    this.reviewText = this.form.locator('[name="review"]');
    this.submitButton = this.form.getByRole("button", { name: "SUBMIT REVIEW" });
    this.reviews = page.locator(".product-reviews .review");
  }

  async scrollToReviews() {
    // WOW keeps the section hidden until scrolling triggers its animation.
    await this.tabs.scrollIntoViewIfNeeded();
  }

  async openReviews() {
    await this.reviewTab.click();
  }
}

export default productReview;
