# Playwright framework and spec presentation guide

This guide describes the code currently in this project. Use the quoted paragraphs as speaking notes and the walkthroughs when presenting files in your editor. It describes implemented checks, not a claim that the latest test run passed.

## 1. Opening introduction — about one minute

> “This project automates customer workflows in an online shopping application using JavaScript and Playwright Test. It covers authentication, product search, cart calculations, wishlists, reviews, profile and billing updates, purchasing, and order tracking. I use Page Object Model to separate page details from test scenarios, JSON for reusable test data, and fixtures for repeated account setup and cleanup. Tests produce an HTML report, and a Jenkins pipeline can run the suite and publish that report.”

## 2. Suggested presentation sequence — 12 to 15 minutes

| Time | What to show | Main point |
| --- | --- | --- |
| 1 minute | Project introduction | Business workflows being tested |
| 2 minutes | Folder structure and configuration | How the framework is organized |
| 2 minutes | Authentication setup and shopping fixture | How each scenario gets its starting state |
| 4 minutes | `purchaseAndTrackOrder.spec.js` | Complete business journey |
| 2 minutes | `repeatedAddToCart.spec.js` and `cartVerification.js` | Strong assertions and cleanup |
| 2 minutes | Execution commands, HTML report, Jenkinsfile | How tests run and how failures are investigated |
| 1–2 minutes | Limitations and questions | What the framework proves and where it can improve |

## 3. Framework structure

```text
playwrightProject1/
|-- playwright.config.js             Execution settings and project selection
|-- package.json                     Dependencies; currently no npm scripts
|-- Jenkinsfile                      Windows Jenkins pipeline and HTML publication
|-- POM/                             Page locators and reusable page operations
|-- testData/
|   `-- testData.json                 User, address, product and expected-result data
|-- tests/
|   |-- auth.setup.js                Shared-account login and storage-state creation
|   |-- AUTHENTICATION.md            Authentication-specific instructions
|   |-- *.spec.js                    Eleven business scenario files
|   `-- support/
|       |-- shopping.fixture.js      Unique-account setup and session teardown
|       `-- cartVerification.js      Shared cart assertions
|-- Manual_Test_Scripts.xlsx          Manual test workbook supplied with the project
`-- screenshots/                     Tracking popup screenshots
```

During execution, the framework also uses `playwright/.auth/user.json` for saved authentication, `playwright-report/` for the HTML report, and `test-results/` for test artifacts when generated. Saved authentication contains session credentials; keep it private when presenting.

> “The spec describes the scenario and expected results. The page objects describe how to find elements and perform reusable actions. The fixture prepares an account, and the data file supplies inputs. This separation makes the tests easier to explain and maintain.”

### How the layers connect

```text
Jenkins or a local Playwright command
                |
                v
playwright.config.js -> selected project and authentication strategy
                |
                v
spec file -> page objects -> application UI
    |              |
    |              +-- locators and reusable operations
    +-- fixtures, JSON inputs and assertion helpers
                |
                v
assertions -> test result -> HTML report and available artifacts
```

### Technologies and design choices

| Component | Use in this project |
| --- | --- |
| JavaScript | Test scenarios, page classes and support code |
| Playwright Test | Test runner, browser fixtures, assertions, hooks and reporting |
| Page Object Model (POM) | Centralizes page locators and some reusable interactions |
| JSON data | Separates reusable inputs and expected values from many test steps |
| Custom fixtures | Registers and logs in a unique shopper for six specs |
| Storage state | Reuses shared-account cookies and local storage for two specs |
| Jenkins | Installs dependencies, runs tests and publishes HTML results |

The configuration uses CommonJS `require` and `module.exports`. Test and POM files use `import` and `export` syntax handled by Playwright's loading pipeline. This is a JavaScript framework; it is not a TypeScript test suite.

## 4. Explain `playwright.config.js`

| Setting | Current behavior | How to explain it |
| --- | --- | --- |
| Environment loading | Loads `.env` if present | Local configuration can be supplied outside test code |
| `BASE_URL` | Required; must be HTTP or HTTPS | Stops early if the application address is missing or invalid |
| Base path | Adds a trailing slash when needed | Keeps relative URLs inside the application's subdirectory |
| `testDir` | `./tests` | Defines where Playwright discovers tests |
| `fullyParallel` | `true` | Allows parallel scheduling, subject to the worker limit |
| `workers` | `1` | Actual execution uses one worker, protecting shared account data |
| `forbidOnly` | Enabled when `CI` is truthy | Prevents a committed `test.only` from silently limiting CI coverage |
| `retries` | Two on CI, zero locally | CI can retry a failed test up to twice |
| Reporter | HTML | Generates a navigable test report |
| Default trace | `on-first-retry` | Captures a trace on the first retry |

Three projects are active:

1. **`setup`** runs `auth.setup.js` using Desktop Chrome settings.
2. **`chromium-authenticated`** depends on setup, loads the saved state, and runs only `paymentPending.spec.js` and `updateBillingAddress.spec.js`.
3. **`chromium`** runs the other nine specs without saved authentication.

Firefox, WebKit, mobile devices and branded browser examples are commented out. Describe current execution as Chromium coverage. `fullyParallel: true` does not mean this suite currently runs several tests at once because `workers: 1` limits concurrency.

Six fixture-based specs override artifact settings with `screenshot: "only-on-failure"` and `trace: "retain-on-failure"`, and set a 60-second timeout. Those overrides are not applied to every spec. With zero local retries, the default `on-first-retry` trace setting alone does not produce a local failure trace.

## 5. Explain authentication and test isolation

### A. Reusing the shared account: `auth.setup.js`

The setup test:

1. Opens `login.php` and logs in using `testData.user`.
2. Checks that the logout link is visible.
3. Opens `my-account.php` and verifies the profile email matches the intended user.
4. Creates the authentication directory and saves browser storage state.

> “I verify the logged-in account before saving its session. The authenticated project depends on this setup, so it receives freshly created state when run normally. Each test still gets its own browser context, but they act on the same server-side account.”

Storage state saves cookies and local storage here. It does not create a database snapshot, save addresses itself, or isolate shared server-side records. The shared account must already exist. Avoid logging it out in a scenario that reuses this saved session.

### B. Creating an independent shopper: `shopping.fixture.js`

The custom `test` extends Playwright's standard test fixture:

1. The `session` fixture creates a `loginLogout` page object and installs a dialog handler.
2. The `shopping` fixture generates an email with `randomUUID()`.
3. It registers that account and asserts the registration confirmation.
4. It logs in and asserts that the logout link is visible.
5. `await use({ session, account })` passes the prepared objects to the scenario.
6. Scenario `afterEach` hooks run their cleanup.
7. Session fixture teardown opens `logout.php` if the page is still open.

> “The fixture removes repeated registration and login steps from the scenario. A unique email reduces collisions with earlier runs. Code before `use` prepares the test; code after `use` performs teardown.”

These six specs use it: login/logout, repeated cart additions, wishlist persistence, wishlist to cart, product review, and profile update. Merely declaring `shopping` in the test arguments activates the fixture, even when the body does not read it.

Unique accounts are not deleted by fixture teardown. Logout and cart or wishlist cleanup do not remove account records. Reviews also remain because the code has no confirmed review-delete UI.

## 6. Complete main spec walkthrough: `purchaseAndTrackOrder.spec.js`

### Business objective

> “This test demonstrates a customer registering, buying products from four categories, entering addresses, submitting a payment option, and opening tracking information for each resulting order.”

### Block 1 — imports

- `test` and `expect` define the scenario and assertions.
- `randomUUID` generates a unique account email.
- `fs` and `path` create the screenshot directory and build output paths.
- `testData` supplies user information, addresses, expected order count and screenshot naming.
- POM imports provide registration, sign-in, categories, addresses, checkout, payment, tracking and logout elements.

### Block 2 — test declaration and data preparation

```javascript
test("complete a purchase and track orders", async ({ page }) => {
```

`page` is supplied by Playwright. The asynchronous function allows each browser operation to be awaited. The test reads the data groups and builds a unique email using the configured prefix, a UUID and the configured domain.

> “I generate a different email for every run so registration can run again without reusing an existing account.”

### Block 3 — handle application dialogs

The `page.on("dialog", ...)` listener logs the dialog text and accepts the dialog. It is installed before actions that can trigger alerts or confirmations.

Accepting an alert lets execution continue; logging its message is not an assertion that the message is correct.

### Block 4 — create page objects

The spec instantiates each required page class with the same `page`. Their locators refer to elements in that browser tab as it navigates through the application.

> “Creating a page object does not open another browser page. It gives this spec named access to elements and operations on the current page.”

### Block 5 — register and log in

The test opens the application using `page.goto("./")`, clicks Login, fills the registration form, submits it, then signs in with the newly generated email and configured password.

This spec handles registration directly. It does not use the shopping fixture or the shared storage-state setup.

### Block 6 — add products from four categories

The scenario opens Books, Fashion, Furniture and Electronics, clicking the configured product's Add to cart button in each category.

The category POMs target specific named products. Despite the older comment in another spec, the book locator is not simply “the first product.” This flow depends on the catalog retaining those products and category links.

### Block 7 — enter billing and shipping addresses

The spec fills and submits billing details, fills and submits shipping details, then reapplies billing details before checkout. Explain this as the current implemented sequence; the code alone does not establish why the application needs the extra billing update.

Naming detail when presenting the editor:

- `shipping.page.js` actually contains **billing** field locators.
- `biiling.page.js` actually contains **shipping** field locators.
- `updateBillling.page.js` handles the separate billing-update scenario.

Point to the actual fields rather than relying on these filenames to explain their responsibility.

### Block 8 — checkout and payment selection

The test clicks the checkout button, selects Internet Banking, and submits the payment form.

> “This automates the application's payment-option submission. The test does not verify a real banking transaction, a payment gateway callback, or a settlement.”

### Block 9 — verify tracking link count

```javascript
await expect(trackPage.trackLink).toHaveCount(
  testData.purchaseAndTrackOrder.expectedOrderCount
);
```

This is the main explicit business assertion in the purchase flow: the number of tracking links must match the configured expected order count. Action success alone does not prove that every intermediate business result is correct.

### Block 10 — open tracking popups and capture screenshots

```javascript
const [popup] = await Promise.all([
  page.waitForEvent("popup"),
  trackPage.trackLink.nth(i).click(),
]);
```

The popup listener is registered before clicking, preventing a timing race where the new window opens before the test starts listening. `Promise.all` waits for both the click and popup event. Destructuring takes the popup result from the first promise.

For every link, the test waits for the popup to load, takes a full-page screenshot in the configured folder, and closes the popup. `nth(i)` selects each matching tracking link by its zero-based position.

These screenshots are files written directly to the configured folder. They are not explicitly attached to the HTML report by this spec, and their contents are not asserted. Repeated runs can overwrite files when the configured names are reused.

### Block 11 — logout

The scenario clicks Logout after the tracking loop. This is the final action in the test body, so an earlier failure can prevent that logout from running. It does not have the fixture teardown used by the six shopping-fixture specs.

### One-minute spoken walkthrough

> “I begin by preparing the input data and generating a unique customer email. I install a dialog handler and create page objects for the pages involved. Then I register and sign in, add one named product from each of four categories, and submit billing and shipping details. I proceed to checkout, select Internet Banking and submit the form. I verify the expected number of tracking links, then open each tracking popup, save a screenshot and close it. Finally, I log out. The main explicit assertion here is the tracking-link count; stronger product, order-status and payment-confirmation checks would improve this flow.”

## 7. Explain every other spec

### `searchProduct.spec.js` — product discovery

**Starting state:** Standard Playwright page without saved login.

**Steps:** Open the store, search for `TV`, verify the search-result URL, find the exact configured TV title, click it, and verify the product heading.

**What it proves:** The selected TV appears for the search and opens the expected detail page. It does not verify all results, sorting, empty searches or no-result behavior. `POM/searchProduct.page.js` stores the locators and page actions; `testData.searchProduct` supplies the home path, keyword, product title and expected URL pattern. The spec keeps the scenario and assertions.

### `loginLogout.spec.js` — TC-010

**Starting state:** The shopping fixture registers and logs in a unique user.

**Steps:** Check the welcome name, open the account page and verify the email, log out, check the signed-out header, then reopen and reload the account page.

**Assertions:** Welcome text and profile identity are correct; Login appears; Logout is absent; the reopened account email field is empty.

**What it proves:** The tested UI no longer exposes the logged-in account state after logout. It does not directly replay an old session cookie against an API to verify server-side token invalidation.

### `changePassword.spec.js` — negative password-change scenario

**Starting state:** Logs in manually using the shared user's existing credentials.

**Steps:** Open the password form, enter an incorrect current password and matching new-password fields, submit, capture the dialog, check the expected error, log out, then log in again with the original password.

**Assertions:** `expect.poll` waits for the captured message to equal the expected error; the password form can still be displayed; the original password still allows login.

**What it proves:** The invalid-current-password attempt is rejected and the original password remains usable. This is not a successful password-change test.

### `paymentPending.spec.js` — incomplete checkout

**Starting state:** Loads saved shared-account authentication after setup.

**Steps:** Verify login, add the named book, proceed to checkout, navigate to My Account instead of submitting payment, and open Payment Pending Order.

**Assertions:** Pending-orders URL matches the expected path and the expected product heading is visible.

**Limit:** It selects the last matching heading. An existing pending order with the same product could satisfy the visibility check; it does not uniquely identify the newly created order. There is no pending-order cleanup in this spec.

### `updateBillingAddress.spec.js` — persisted billing details

**Starting state:** Loads saved shared-account authentication after setup.

**Steps:** Open My Account, Shipping / Billing Address and the billing section; update address, state and city; submit and reload.

**Assertions:** Those three fields contain the configured updated values after reload.

**Limit:** The title in the code is currently `"pending payment"`, although the scenario updates billing details. The spec does not update or verify the pincode and does not restore the previous address.

### `repeatedAddToCart.spec.js` — TC-005

**Starting state:** Unique logged-in shopper from the fixture.

**Steps:** Add the book once and verify quantity one, add it twice more, verify one product row with quantity three, then reload and verify again.

**Assertions:** No duplicate product rows; unit price stays unchanged; quantity and monetary totals are correct; state survives refresh.

**Cleanup:** `afterEach` clears the cart and asserts the empty-cart message. The POM supplies required address fields because they share the cart form and are needed to submit removal.

### `wishlistPersistence.spec.js` — TC-006

**Starting state:** Unique logged-in shopper from the fixture.

**Steps:** Open the correct product, save it to the wishlist, verify it after reload, log out, log back in with the same account, and reopen the wishlist.

**Assertions:** Correct product heading, one matching wishlist row, expected wishlist URL and login state, and the product still exists after a new login.

**Cleanup:** Removes the matching wishlist entry and checks that no matching rows remain.

### `wishlistToCart.spec.js` — TC-007

**Starting state:** Unique logged-in shopper from the fixture.

**Steps:** Save the book to the wishlist, read its current price while excluding the old-price span, add the saved product to the cart, compare prices, reload and check the cart, then open the cart's product link.

**Assertions:** Matching wishlist row, quantity one, correct cart totals, same wishlist and cart unit price, refresh persistence and correct product destination.

**Cleanup:** Separate hooks clear the cart and wishlist, so wishlist cleanup is still attempted if the cart cleanup fails.

**Limit:** The scenario adds a wishlist product to the cart. It does not assert that adding it automatically removes it from the wishlist.

### `productReview.spec.js` — TC-008

**Starting state:** Unique logged-in shopper from the fixture.

**Steps:** Open the expected product, scroll to the review section, open the tab, set quality/price/value ratings to four, enter a name and UUID-based review summary, attach the summary and product URL to the result, submit and reopen the same product's reviews.

**Assertions:** Correct product, visible form, checked rating controls, successful HTTP response, exactly one review matching the unique summary, and matching reviewer name and review text.

The response listener is registered before submission. The unique summary avoids accidentally matching an older review. Scrolling is needed because the page animation can keep the review section hidden until it enters view.

**Limit:** It checks selected rating controls before submission but does not assert persisted rating values afterward. The posted review remains in the application because there is no confirmed deletion UI in this implementation.

### `updateProfile.spec.js` — TC-009

**Starting state:** Unique logged-in shopper from the fixture.

**Steps:** Save the original name and contact, update them, reload, verify the fields and unchanged email, log out and back in, then verify the new profile and welcome name again.

**Assertions:** Name and contact persist through reload and login, email matches the generated account, and the welcome header reflects the updated name.

**Cleanup:** Restores the original name and contact, reloads, and verifies restoration.

## 8. Explain shared assertions and Playwright concepts

### Cart calculation helper

`tests/support/cartVerification.js` centralizes assertions used by both cart specs. `checkCart(cart, quantity)` checks one matching row and one quantity input, verifies the expected quantity, converts displayed money to numbers, and checks:

```text
unit price > 0
row total = expected quantity × unit price + displayed shipping
grand total = row total
```

`toBeCloseTo(..., 2)` allows a small floating-point tolerance when comparing monetary values. The helper returns the unit price so a spec can compare it with another observation. These checks assume a one-product cart, including only one quantity input across the page; they are not a general multi-product cart calculator.

> “I reuse the calculation checks so both cart scenarios enforce the same expected arithmetic. Assertions stay in tests and support code; the page objects supply elements and actions.”

### Terms to explain simply

| Term | Explanation in this framework |
| --- | --- |
| Spec | A file defining an executable business scenario |
| Locator | A reusable description of how to find an element |
| `async` / `await` | Waits for asynchronous browser operations before continuing |
| `expect(locator)` | Retries supported UI assertions until they pass or time out |
| `expect(number)` | Checks a value already read; does not reread the UI automatically |
| `expect.poll` | Repeatedly evaluates a callback, used here for a dialog message |
| Fixture | Supplies prepared test resources and can manage teardown |
| `afterEach` | Cleanup hook that runs after the scenario, including after test failure |
| Browser context | An isolated browser session; it does not isolate server-side data |
| Trace | Recorded browser activity useful for diagnosing failures |
| POM composition | One page object contains others, as in wishlist-to-cart |

Locators in this project include XPath, CSS, roles, placeholders, exact text and filtered product rows. The framework has no fixed `waitForTimeout` sleeps in the reviewed spec and support files; it uses action waits, assertions, and explicit URL, response, dialog and popup waits instead. That improves synchronization, but it does not guarantee every scenario is free of timing issues.

## 9. Running and demonstrating the work

Run commands from the project root. These examples use `npx.cmd` and `npm.cmd` to work conveniently in Windows PowerShell.

```powershell
# Install dependencies and browser binaries when setting up the project.
npm.cmd install
npx.cmd playwright install

# Supply the actual application root, including its subdirectory if applicable.
# Alternatively, set BASE_URL in the local .env file.
$env:BASE_URL = "https://your-test-host.example/shopping/"

# List discovered tests without executing browser scenarios.
npx.cmd playwright test --list

# Run the complete suite, including required authentication setup.
npx.cmd playwright test

# Demonstrate the main purchase flow in a visible browser.
npx.cmd playwright test tests/purchaseAndTrackOrder.spec.js --project=chromium --headed

# Demonstrate a smaller assertion-rich scenario.
npx.cmd playwright test tests/repeatedAddToCart.spec.js --project=chromium --headed

# Run specs that reuse the shared account; setup runs as a dependency.
npx.cmd playwright test --project=chromium-authenticated

# Open the generated HTML report.
npx.cmd playwright show-report
```

Use the application's real test environment in place of the placeholder. The shared account must exist for setup, and the catalog and test data must match the environment. Do not show passwords or saved session contents during the presentation.

There is currently no `npm test` script in `package.json`; use the Playwright command directly. Avoid `--no-deps` for authenticated runs unless deliberately reusing an existing session file.

### Practical demo sequence

1. Open this guide and explain the business scope.
2. Show `playwright.config.js`, especially the three projects and single worker.
3. Show one simple locator POM and one POM with reusable methods.
4. Walk through the purchase spec using section 6.
5. Run a small headed scenario, then show its actual result in the HTML report.
6. Show cart assertions and cleanup to demonstrate verification depth.
7. If available from a run, show a trace and the tracking screenshots, explaining how each was captured.

## 10. Explain `Jenkinsfile`

> “The pipeline obtains the application URL from the Jenkins credential named `Project_BaseURL`. It installs the project dependencies and Playwright browsers, runs the suite, and uses the HTML Publisher plugin to publish the report when the report exists. Publication is attempted in the `always` post block, including when tests fail.”

The file uses `bat`, so it expects a Windows-capable agent even though the agent selector is `any`. `PLAYWRIGHT_HTML_OPEN=never` prevents the report from automatically opening during the build.

The configuration enables retries and `forbidOnly` when `process.env.CI` is truthy. The Jenkinsfile does not explicitly set `CI`, so explain those settings as conditional on the agent environment rather than guaranteed by this pipeline alone.

The presence of the Jenkinsfile proves that pipeline configuration exists. It does not prove that a Jenkins build has run successfully; use an actual build result if making that claim.

## 11. Questions you may be asked

**Why use Page Object Model?**

> “It gives locators and reusable interactions a clear home. A locator change can often be handled in a page object instead of changing every test.”

**Is all test data externalized?**

> “Reusable user, address, search and expected-result data is in JSON. Some values remain in other specs or POMs, including profile-update values and cleanup addresses. Externalization is partial.”

**Why use both saved login and generated accounts?**

> “Saved login supports scenarios using an existing shared account. Generated accounts support independent shopping scenarios and explicit login/logout behavior. They solve different starting-state needs.”

**Why only one worker?**

> “Some specs change the same server-side account. One worker reduces interference. More parallel execution would need stronger isolation, especially separate accounts and cleanup.”

**How do you verify persistence?**

> “I reload and reassert cart, review and billing values. Wishlist and profile scenarios also log out and log back in before checking the saved state.”

**How do you handle popups and alerts?**

> “I register listeners before the triggering action. Dialog handlers accept alerts, and popup handling waits for the new page, captures it and closes it.”

**Does the suite cover multiple browsers?**

> “The active projects use Chromium. Other browser and mobile examples exist in the config but are commented out.”

**Do retries mean a failure is fixed?**

> “No. They provide another execution attempt and can help collect diagnostics. A retry pass still needs investigation if it signals unstable behavior.”

**What would you improve next?**

> “I would strengthen the purchase assertions, identify new pending orders uniquely, standardize filenames and titles, improve shared-account cleanup, and add additional browser coverage once the data is isolated.”

## 12. Current limitations and concrete improvements

| Observed implementation | Useful next improvement |
| --- | --- |
| Purchase flow mainly asserts tracking-link count | Verify cart contents, address persistence, order identity and confirmation/status |
| Tracking popups are captured as screenshots | Assert product/order/status details and attach evidence to the test result |
| Pending-payment check can match an older product entry | Capture an order identifier and assert that specific new record |
| Shared-account specs retain changed billing/pending data | Restore original values and remove scenario-created records where supported |
| Unique accounts and reviews remain after tests | Add supported record cleanup or a controlled test-data reset |
| Purchase logout is only at the end of the test body | Move session cleanup into teardown that also runs on failure |
| Billing-related filenames and a test title are misleading | Rename them consistently and update imports |
| Locator styles and abstraction depth vary | Adopt consistent naming and reusable operations where they add value |
| Only Chromium is active | Add other browsers after checking environment and data isolation |
| Jenkins uses `npm install` and relies on environment for CI flags | Consider reproducible dependency installation with a committed lockfile and explicit CI configuration |

## 13. Closing statement

> “The framework covers the main shopping journeys and separates business scenarios from page details. Reusable account setup, persistence checks, cart calculations and cleanup make several scenarios repeatable and verifiable. The report and Jenkins configuration support execution and investigation. My next priorities are stronger purchase and tracking assertions and more complete control of server-side test data.”

## 14. Preparation checklist

- Confirm the test environment is reachable and the catalog matches the locators.
- Confirm the shared test account exists if demonstrating authenticated specs.
- Run the chosen demo in advance and present its actual result.
- Keep credentials, `.env` contents and saved authentication out of the screen share.
- Open the relevant spec, its POMs, configuration and report before starting.
- Distinguish an implemented check from a planned improvement when answering questions.
