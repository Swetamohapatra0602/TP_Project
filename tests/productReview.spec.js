import { test, expect } from "./support/shopping.fixture";
import { randomUUID } from "crypto";
import productReview from "../POM/productReview.page";

test.use({ screenshot: "only-on-failure", trace: "retain-on-failure" });
test.setTimeout(60000);

test("TC-008 submit a review and verify product-specific persistence", async ({ page, shopping }, testInfo) => {

  const reviewPage = new productReview(page);
  const summary = `Review-${randomUUID()}`;
  const reviewText = `Automated review for ${reviewPage.product.productName}. ${summary}`;
  await reviewPage.product.open();
  await expect(reviewPage.product.productHeading).toHaveText(reviewPage.product.productName);
  const productURL = page.url();
  await reviewPage.scrollToReviews();
  await expect(reviewPage.reviewTab).toBeVisible();
  await reviewPage.openReviews();
  await expect(reviewPage.form).toBeVisible();
  for (const rating of reviewPage.ratings) {
    await rating.check();
    await expect(rating).toBeChecked();
  }
  await reviewPage.name.fill("Workflow Reviewer");
  await reviewPage.summary.fill(summary);
  await reviewPage.reviewText.fill(reviewText);
  // No confirmed review-delete UI; retain the unique identifier as evidence.
  await testInfo.attach("review-identifier", {
    body: JSON.stringify({ summary, productURL }), contentType: "application/json",
  });
  const submitted = page.waitForResponse(r => r.request().method() === "POST" && r.url().includes("product-details.php"));
  await reviewPage.submitButton.click();
  expect((await submitted).ok()).toBeTruthy();
  await page.goto(productURL);
  await reviewPage.scrollToReviews();
  await expect(reviewPage.reviewTab).toBeVisible();
  await reviewPage.openReviews();
  await expect(reviewPage.form).toBeVisible();
  const review = reviewPage.reviews.filter({ hasText: summary });
  await expect(review).toHaveCount(1);
  await expect(review).toContainText("Workflow Reviewer");
  await expect(review).toContainText(reviewText);
});
