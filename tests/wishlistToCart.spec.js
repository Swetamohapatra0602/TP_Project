import { test, expect } from "./support/shopping.fixture";
import wishlistToCart from "../POM/wishlistToCart.page";
import { checkCart } from "./support/cartVerification";

test.use({ screenshot: "only-on-failure", trace: "retain-on-failure" });
test.setTimeout(60000);

let wishlist;
let cart;

test("TC-007 add a wishlist product to cart", async ({ page, shopping }) => {
  const session = shopping.session;

  const workflow = new wishlistToCart(page);
  wishlist = workflow.wishlist;
  cart = workflow.cart;

  // Open the book and save it to the wishlist.
  await wishlist.product.open();
  await expect(wishlist.product.productHeading).toHaveText(wishlist.product.productName);
  await wishlist.saveToWishlist();
  await expect(session.logoutLink).toBeVisible();
  await expect(wishlist.wishlistRow).toHaveCount(1);

  // Read the current price. The old price is inside a separate span.
  const priceText = await workflow.price.evaluate(function (element) {
    return element.firstChild.textContent;
  });
  const priceWithoutCurrency = priceText.replace("Rs.", "").trim();
  const priceWithoutCommas = priceWithoutCurrency.replaceAll(",", "");
  const wishlistPrice = Number(priceWithoutCommas);

  // Add the book to the cart and compare its price.
  await workflow.addSavedProduct();
  const cartPrice = await checkCart(cart, 1);
  expect(cartPrice).toBe(wishlistPrice);

  // Check that the cart still has one book after refreshing.
  await page.reload();
  await checkCart(cart, 1);

  // Check that the cart link opens the correct book.
  await cart.productLink.click();
  await expect(cart.product.productHeading).toHaveText(cart.product.productName);
});

test.afterEach(async ({ page }) => {
  if (page.isClosed() || !cart) {
    return;
  }

  // Remove the book from the cart after the test.
  await cart.clearCart();
  await expect(cart.emptyCart).toBeVisible();
});

test.afterEach(async ({ page }) => {
  if (page.isClosed() || !wishlist) {
    return;
  }

  // Use a separate hook so this runs even if cart cleanup fails.
  await wishlist.clearWishlist();
  await expect(wishlist.wishlistRow).toHaveCount(0);
});
