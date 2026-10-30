import { test, expect } from "@playwright/test";

test("search for a TV and open its product details", async ({ page }) => {
  const productName = "Micromax 81cm (32) HD Ready LED TV  (32T6175MHD, 2 x HDMI, 2 x USB)";

  // Open the store and search for a TV.
  await page.goto("./");
  await page.getByPlaceholder("Search here...").fill("TV");
  await page.locator('form[name="search"] button[name="search"]').click();

  // Verify the expected TV appears in the search results.
  await expect(page).toHaveURL(/\/search-result\.php(?:\?.*)?$/);
  const television = page.locator(".product").getByRole("link", {
    name: productName,
    exact: true,
  });
  await expect(television).toBeVisible();

  // Open the result and confirm it is the correct product.
  await television.click();
  await expect(page.locator("h1")).toHaveText(productName);
});
