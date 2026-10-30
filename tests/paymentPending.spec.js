import { test, expect } from "@playwright/test";
import testData from "../testData/testData.json";
import Book from "../POM/book.page";
import proceedToCheckOut from "../POM/proceedToCheckOut.page";
import myAccount from "../POM/myAccount.page";

test("pending payment", async ({ page }) => {
  //here we are loggin in using already saved login,shipping and billing.
  // we will go to checkout and then click myaccount and go to payment pending page.there the product should be shown

  page.on("dialog", async (dialog) => {
    console.log(await dialog.message());
    await dialog.accept();
  });

  let BookPage = new Book(page);
  let proceedToCheckOutPage = new proceedToCheckOut(page);
  let myAccountPage = new myAccount(page);

  // Reuse the authenticated session created by auth.setup.js.
  await page.goto("./");
  await expect(page.locator('a[href="logout.php"]')).toBeVisible();

  //book(choose category,click on add to cart for first element)
  await BookPage.bookCategory.click();
  await BookPage.addToCart.click();

  //Shipping
  // await shippingPage.billingaddress.fill("bangalore")
  // await shippingPage.bilingstate.fill("KT")
  // await shippingPage.billingcity.fill("Bang")
  // await shippingPage.billingpincode.fill("123456")
  // await shippingPage.updateButton.click()

  //Proceed  to checkout
  await proceedToCheckOutPage.checkoutButton.click();

  //click on my account to inturrupt
  await myAccountPage.myAccountHome.click();

  //click on pending payment
  await myAccountPage.PaymentPendingLink.click();

  //It should show the product
  await expect(page).toHaveURL(testData.paymentPending.pendingOrdersPath);
  let x = page
    .getByRole("heading", {
      name: testData.paymentPending.productName,
      exact: true,
    })
    .last();
  await expect(x).toBeVisible();
});
