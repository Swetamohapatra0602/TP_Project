import testData from "../testData/testData.json";

class updateProfile {
  constructor(page) {
    this.page = page;
    this.name = page.locator("#name");
    this.contact = page.locator("#contactno");
    this.email = page.locator("#exampleInputEmail1");
    this.updateButton = page.locator('button[name="update"]');
    this.welcomeName = page.locator(".cnt-account").getByText("Welcome -Manual Profile Check", { exact: true });
  }

  async open() {
    await this.page.goto("my-account.php", { waitUntil: "domcontentloaded" });
  }

  async update(name, contact, session) {
    await this.name.fill(name);
    await this.contact.fill(contact);
    const confirmation = this.page.waitForEvent("dialog");
    await this.updateButton.click();
    await confirmation;
    await session.dialogHandled;
    await this.page.waitForLoadState("domcontentloaded");
  }
}

export default updateProfile;
