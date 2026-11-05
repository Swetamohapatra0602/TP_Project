import { test, expect } from "./support/shopping.fixture";
import repeatedAddToCart from "../POM/repeatedAddToCart.page";
import { checkCart } from "./support/cartVerification";

test.use({ screenshot: "only-on-failure", trace: "retain-on-failure" });
test.setTimeout(60000);

let cart;

test("TC-005 repeated Add to Cart updates quantity and totals", async ({ page, shopping }) => {

  cart = new repeatedAddToCart(page);
  await cart.addBook();
  await expect(cart.cartRow).toHaveCount(1);
  const unitPrice = await checkCart(cart, 1);
  await cart.addBook();
  await expect(cart.cartRow).toHaveCount(1);
  await cart.addBook();
  await expect(cart.cartRow).toHaveCount(1);
  expect(await checkCart(cart, 3)).toBe(unitPrice);
  await page.reload();
  await checkCart(cart, 3);
});

test.afterEach(async ({ page }) => {
  if (page.isClosed() || !cart) return;
  await cart.clearCart();
  await expect(cart.emptyCart).toBeVisible();
});


/*After every test, I check whether the browser page is closed or the cart object is unavailable.
 If either condition is true, I skip the cleanup. 
 Otherwise, I clear the shopping cart and verify that the empty cart message is visible. 
 This ensures test isolation and prevents test data from affecting subsequent test cases.*/