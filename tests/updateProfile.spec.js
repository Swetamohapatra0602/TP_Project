import { test, expect } from "./support/shopping.fixture";
import updateProfile from "../POM/updateProfile.page";

test.use({ screenshot: "only-on-failure", trace: "retain-on-failure" });
test.setTimeout(60000);

let profile, original;

test("TC-009 update profile and verify persistence across login", async ({ page, shopping }) => {
  const { session, account } = shopping;

  profile = new updateProfile(page);
  await profile.open();
  original = { name: await profile.name.inputValue(), contact: await profile.contact.inputValue() };
  await profile.update("Manual Profile Check", "9876543210", session);
  await page.reload();
  await expect(profile.name).toHaveValue("Manual Profile Check");
  await expect(profile.contact).toHaveValue("9876543210");
  await expect(profile.email).toHaveValue(account.email);
  await session.logout();
  await expect(session.loginLink).toBeVisible();
  await expect(session.logoutLink).toHaveCount(0);
  await session.login(account);
  await expect(session.logoutLink).toBeVisible();
  await profile.open();
  await expect(profile.name).toHaveValue("Manual Profile Check");
  await expect(profile.contact).toHaveValue("9876543210");
  await expect(profile.welcomeName).toBeVisible();
});

test.afterEach(async ({ page, shopping }) => {
  if (page.isClosed() || !original) return;
  await profile.open();
  await profile.update(original.name, original.contact, shopping.session);
  await page.reload();
  await expect(profile.name).toHaveValue(original.name);
  await expect(profile.contact).toHaveValue(original.contact);
});
