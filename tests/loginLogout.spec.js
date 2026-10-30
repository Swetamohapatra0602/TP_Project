import { test, expect } from "./support/shopping.fixture";
import testData from "../testData/testData.json";

test.use({ screenshot: "only-on-failure", trace: "retain-on-failure" });
test.setTimeout(60000);

test("TC-010 valid login and logout invalidate the session", async ({ page, shopping }) => {
  const { session: loginPage, account } = shopping;

  // The fixture registers a unique account and signs in before this test.
  const welcomeMessage = loginPage.accountHeader.getByText(`Welcome -${account.name}`, { exact: true });
  await expect(welcomeMessage).toBeVisible();
  await loginPage.open("my-account.php");
  await expect(loginPage.profileEmail).toHaveValue(account.email);

  // Sign out and verify the header returns to the signed-out state.
  await loginPage.logout();
  await expect(loginPage.loginLink).toBeVisible();
  await expect(loginPage.logoutLink).toHaveCount(0);

  // Reopening a protected page must require login again.
  await loginPage.open("my-account.php");
  await page.reload();
  await expect(loginPage.logoutLink).toHaveCount(0);
  await expect(loginPage.profileEmail).toBeEmpty();
});
