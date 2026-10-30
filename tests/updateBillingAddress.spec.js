import { test, expect } from "@playwright/test";
import testData from "../testData/testData.json";
import myAccount from "../POM/myAccount.page";
import updateBilling from "../POM/updateBillling.page";

test("pending payment", async ({ page }) => {
  //here we are loggin in using already saved login,shipping and billing.
  // we will go to checkout and then click myaccount and go to payment pending page.there the product should be shown

  page.on("dialog", async (dialog) => {
    console.log(await dialog.message());
    await dialog.accept();
  });

  let myAccountPage = new myAccount(page);
  let updateBillingPage = new updateBilling(page);

  // Reuse the authenticated session created by auth.setup.js.
  await page.goto("./");
  await expect(page.locator('a[href="logout.php"]')).toBeVisible();

  //click on my account
  await myAccountPage.myAccountHome.click();

  //click on shipping/Billing Address
  await myAccountPage.ShippingBillingLink.click();

  //Click on update billing
  await updateBillingPage.billingaddresslink.click();
  await updateBillingPage.billingaddressTF.fill(testData.updateBillingAddress.billingAddress.address);
  await updateBillingPage.bilingstateTF.fill(testData.updateBillingAddress.billingAddress.state);
  await updateBillingPage.billingcityTF.fill(testData.updateBillingAddress.billingAddress.city);
  await updateBillingPage.updateButton.click();

  //make sure the billing adress is updated now
  await page.reload();
  await expect(updateBillingPage.billingaddressTF).toHaveValue(testData.updateBillingAddress.billingAddress.address);
  await expect(updateBillingPage.bilingstateTF).toHaveValue(testData.updateBillingAddress.billingAddress.state);
  await expect(updateBillingPage.billingcityTF).toHaveValue(testData.updateBillingAddress.billingAddress.city);
});
