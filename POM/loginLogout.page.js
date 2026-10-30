import testData from "../testData/testData.json";
import signin from "./signIn.page";
import signUp from "./signUp.page";

class loginLogout {
  constructor(page) {
    this.page = page;
    this.loginLink = page.locator('a[href="login.php"]');
    this.logoutLink = page.locator('a[href="logout.php"]');
    this.profileEmail = page.locator("#exampleInputEmail1");
    this.accountHeader = page.locator(".cnt-account");
  }

  async open(path) {
    await this.page.goto(path, { waitUntil: "domcontentloaded" });
  }

  async register(account) {
    await this.open("login.php");
    const form = new signUp(this.page);
    await form.fullName.fill(account.name);
    await form.email.fill(account.email);
    await form.contactno.fill(account.contact);
    await form.password.fill(account.password);
    await form.confirmpassword.fill(account.password);
    const confirmation = this.page.waitForEvent("dialog");
    await form.submitButton.click();
    const message = (await confirmation).message();
    await this.dialogHandled;
    return message;
  }

  async login(account) {
    await this.open("login.php");
    const form = new signin(this.page);
    await form.email.fill(account.email);
    await form.password.fill(account.password);
    await form.loginButton.click();
  }

  async logout() {
    await this.logoutLink.click();
  }
}

export default loginLogout;
