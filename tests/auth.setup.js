import { test as setup, expect } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import path from "node:path";
import testData from "../testData/testData.json";
import signin from "../POM/signIn.page";

const authFile = path.resolve(__dirname, "../playwright/.auth/user.json");

setup("authenticate the shared account", async ({ page }) => {
  await page.goto("login.php");
  const signInPage = new signin(page);
  await signInPage.email.fill(testData.user.email);
  await signInPage.password.fill(testData.user.password);
  await signInPage.loginButton.click();
  await expect(page.locator('a[href="logout.php"]')).toBeVisible();

  // Confirm the authenticated account before saving its session.
  await page.goto("my-account.php");
  await expect(page.locator("#exampleInputEmail1")).toHaveValue(testData.user.email);
  await mkdir(path.dirname(authFile), { recursive: true });
  await page.context().storageState({ path: authFile });
});
