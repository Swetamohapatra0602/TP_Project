import { test as base, expect } from "@playwright/test";
import { randomUUID } from "crypto";
import testData from "../../testData/testData.json";
import loginLogout from "../../POM/loginLogout.page";

export const test = base.extend({
  // Keep session teardown separate so logout also runs if account setup fails.
  session: async ({ page }, use) => {
    const session = new loginLogout(page);
    page.on("dialog", dialog => {
      session.dialogHandled = dialog.accept();
      // Actions expecting confirmation await this promise. Handle page closure
      // without leaving an unhandled rejection from the dialog listener.
      session.dialogHandled.catch(() => {});
    });

    await use(session);

    // Fixture teardown runs after scenario afterEach hooks finish their cleanup.
    if (!page.isClosed()) await session.open("logout.php");
  },

  shopping: async ({ session }, use) => {
    const account = {
      name: "Workflow Tester",
      email: `workflow-${randomUUID()}@${testData.user.emailDomain}`,
      contact: testData.user.contactNumber,
      password: testData.user.password,
    };
    const registrationMessage = await session.register(account);
    expect(registrationMessage).toContain("successfully register");
    await session.login(account);
    await expect(session.logoutLink).toBeVisible();

    await use({ session, account });
  },
});

export { expect };
