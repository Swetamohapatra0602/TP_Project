import { test, expect } from "@playwright/test";
import { randomUUID } from "crypto";
import fs from "fs";
import path from "path";
import testData from "../testData/testData.json";
import loginLink from "../POM/homeLoginlink.page";
import signin from "../POM/signIn.page";
import signUp from "../POM/signUp.page";
import Book from "../POM/book.page";
import Fashion from "../POM/fashion.page";
import Furniture from "../POM/furniture.page";
import Electronics from "../POM/electronics.page";
import shipping from "../POM/shipping.page";
import billing from "../POM/biiling.page";
import proceedToCheckOut from "../POM/proceedToCheckOut.page";
import payment from "../POM/payment.page";
import track from "../POM/trackproduct.page";
import logout from "../POM/logout.page";

test("complete a purchase and track orders", async ({ page }) => {
  const { user } = testData;
  const { billingAddress, shippingAddress, screenshots } = testData.purchaseAndTrackOrder;
  const userEmail = `${user.emailPrefix}-${randomUUID()}@${user.emailDomain}`;

  page.on("dialog", async (dialog) => {
    console.log(dialog.message());
    await dialog.accept();
  });

  const loginPage = new loginLink(page);
  const signUpPage = new signUp(page);
  const signInPage = new signin(page);
  const bookPage = new Book(page);
  const fashionPage = new Fashion(page);
  const furniturePage = new Furniture(page);
  const electronicsPage = new Electronics(page);
  const shippingPage = new shipping(page);
  const billingPage = new billing(page);
  const checkoutPage = new proceedToCheckOut(page);
  const paymentPage = new payment(page);
  const trackPage = new track(page);
  const logoutPage = new logout(page);

  //Register a new account for this run.
  await page.goto("./");
  await loginPage.loginLink.click();
  await signUpPage.fullName.fill(user.fullName);
  await signUpPage.email.fill(userEmail);
  await signUpPage.contactno.fill(user.contactNumber);
  await signUpPage.password.fill(user.password);
  await signUpPage.confirmpassword.fill(user.password);
  await signUpPage.submitButton.click();

  //Sign in.
  await signInPage.email.fill(userEmail);
  await signInPage.password.fill(user.password);
  await signInPage.loginButton.click();

  //Add one product from each category.
  await bookPage.bookCategory.click();
  await bookPage.addToCart.click();

  await fashionPage.FashionCategory.click();
  await fashionPage.addToCart.click();

  await furniturePage.FurnitureCategory.click();
  await furniturePage.addToCart.click();

  await electronicsPage.ElectronicsCategory.click();
  await electronicsPage.addToCart.click();

  //Set the billing address.
  await shippingPage.billingaddress.fill(billingAddress.address);
  await shippingPage.bilingstate.fill(billingAddress.state);
  await shippingPage.billingcity.fill(billingAddress.city);
  await shippingPage.billingpincode.fill(billingAddress.pincode);
  await shippingPage.updateButton.click();

  //Set the shipping address.
  await billingPage.shippingaddress.fill(shippingAddress.address);
  await billingPage.shippingstate.fill(shippingAddress.state);
  await billingPage.shippingcity.fill(shippingAddress.city);
  await billingPage.shippingpincode.fill(shippingAddress.pincode);
  await billingPage.updateButton.click();

  //Reapply the billing address before checkout.
  await shippingPage.billingaddress.fill(billingAddress.address);
  await shippingPage.bilingstate.fill(billingAddress.state);
  await shippingPage.billingcity.fill(billingAddress.city);
  await shippingPage.billingpincode.fill(billingAddress.pincode);
  await shippingPage.updateButton.click();

  //Check out and pay using internet banking.
  await checkoutPage.checkoutButton.click();

  await paymentPage.internetBankingRadio.click();
  await paymentPage.submitButton.click();

  //Capture one tracking screenshot for each purchased product.
  await expect(trackPage.trackLink).toHaveCount(testData.purchaseAndTrackOrder.expectedOrderCount);
  const count = await trackPage.trackLink.count();
  fs.mkdirSync(screenshots.folder, { recursive: true });

  for (let i = 0; i < count; i++) {
    const [popup] = await Promise.all([
      page.waitForEvent("popup"),
      trackPage.trackLink.nth(i).click(),
    ]);

    await popup.waitForLoadState("load");

    await popup.screenshot({
      path: path.join(screenshots.folder, `${screenshots.filenamePrefix}-${i + 1}.png`),
      fullPage: true,
    });

    await popup.close();
  }

  //Sign out.
  await logoutPage.logoutLink.click();
});
