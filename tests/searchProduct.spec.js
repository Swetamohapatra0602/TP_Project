import { test, expect } from "@playwright/test";
import searchProduct from "../POM/searchProduct.page";
import testData from "../testData/testData.json";

test("search for a TV and open its product details", async ({ page }) => {
  const data = testData.searchProduct;
  const searchPage = new searchProduct(page, data.productName);

  // Open the store and search for a TV.
  await searchPage.open(data.homePath);
  await searchPage.search(data.keyword);

  // Verify the expected TV appears in the search results.
  await expect(searchPage.productLink).toBeVisible();

  // Open the result and confirm it is the correct product.
  await searchPage.openProduct();
  await expect(searchPage.productHeading).toHaveText(data.productName);
});
