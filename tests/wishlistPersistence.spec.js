import { test, expect } from "./support/shopping.fixture";
import wishlistPersistence from "../POM/wishlistPersistence.page";

test.use({ screenshot: "only-on-failure", trace: "retain-on-failure" });
test.setTimeout(60000);

let wishlist;

test("TC-006 wishlist persists after logout and login", async ({ page, shopping }) => {
  const { session, account } = shopping;

  wishlist = new wishlistPersistence(page);
  await wishlist.product.open();
  await expect(wishlist.product.productHeading).toHaveText(wishlist.product.productName);
  await wishlist.saveToWishlist();
  await expect(session.logoutLink).toBeVisible();
  await expect(wishlist.wishlistRow).toHaveCount(1);
  await page.reload();
  await expect(page).toHaveURL(wishlist.url);
  await expect(session.logoutLink).toBeVisible();
  await expect(wishlist.wishlistRow).toHaveCount(1);
  await session.logout();
  await expect(session.loginLink).toBeVisible();
  await expect(session.logoutLink).toHaveCount(0);
  await session.login(account);
  await expect(session.logoutLink).toBeVisible();
  await wishlist.open();
  await expect(wishlist.wishlistRow).toHaveCount(1);
  await expect(wishlist.productLink).toBeVisible();
});

test.afterEach(async ({ page }) => {
  if (page.isClosed() || !wishlist) return;
  await wishlist.clearWishlist();
  await expect(wishlist.wishlistRow).toHaveCount(0);
});
