## 01. Online Shopping Automation

This presentation describes the current local project, playwrightProject1. It follows the 21-slide structure and native geometric layouts of the supplied CRM reference. No application brand or client identity is established by the code, so the title uses Online Shopping. The deck documents implemented coverage; it does not claim that the full suite passed. Sources: package.json, playwright.config.js, tests/, POM/.

## 02. Project Information

The application under test is an online shopping website. The repository contains 11 spec files with one business test each, 24 files under POM, and one authentication setup test. Four product categories are used by the purchase workflow: Books, Fashion, Furniture and Electronics. The configured execution projects use Chromium. Client name and deployment ownership are not provided. Sources: package.json; tests/*.spec.js; POM/; playwright.config.js.

## 03. Project Business Need

These are intended benefits of automation, not measured savings. The project uses assertions for customer-visible behavior, persistence and cart calculations. POM classes centralize page details and reusable operations. HTML reports and traces support investigation. Sources: tests/support/cartVerification.js; tests/*.spec.js; playwright.config.js.

## 04. Application Modules

This is a map of UI areas exercised by the automation, not a claim about the application server architecture. Discovery covers search and four categories. The customer can save products, purchase, review products and maintain account details. Sources: POM/ and tests/.

## 05. Framework Architecture

Local CLI commands or CI invoke Playwright Test using playwright.config.js. Specs express scenarios and assertions; page objects provide locators and operations. JSON inputs and fixtures supply data and starting state. Reports and configured artifacts are produced during execution. POM is used with varying depth: some classes are locator holders, others include methods. Sources: playwright.config.js; tests/support/; POM/; testData/testData.json; Jenkinsfile.

## 06. Technology & Structure

This is a JavaScript framework. package.json is CommonJS while specs and POM files use import/export syntax handled by Playwright. package.json has no npm scripts. There are 24 page-object files, 11 spec files and a support directory. Manual_Test_Scripts.xlsx is present, but no manual-to-automated mapping is asserted here. Sources: package.json; project file tree; playwright.config.js.

## 07. Login & Logout

TC-010 uses the shopping fixture to register and sign in a unique shopper. It verifies the welcome message and profile email, signs out, checks that the login link is visible and the logout link is absent, then opens and reloads my-account.php and verifies an empty profile email. This is a UI-level session check. Sources: tests/loginLogout.spec.js; POM/loginLogout.page.js; tests/support/shopping.fixture.js.

## 08. Product Search & Cart

Product search looks up a TV by the JSON-defined search term and verifies the product heading. Repeated Add to Cart opens a specific product and adds it three times. The test checks one row after each addition, and calls checkCart for quantities one and three. checkCart parses currency and checks row total = quantity * unit price + shipping, and grand total equals row total. The formula reflects this application and the current one-product cart. Sources: tests/searchProduct.spec.js; tests/repeatedAddToCart.spec.js; tests/support/cartVerification.js; POM/searchProduct.page.js.

## 09. Wishlist Persistence

TC-006 verifies a product persists in the wishlist after a logout/login cycle using the same generated account. It checks the product heading before saving, then one wishlist row and a visible product link after login. The test does not follow that link to recheck the details heading. The local let wishlist declaration shadows the outer variable, so the afterEach cleanup hook currently returns without cleanup. Sources: tests/wishlistPersistence.spec.js; POM/wishlistPersistence.page.js; tests/support/shopping.fixture.js.

## 10. Wishlist to Cart

TC-007 adds a saved wishlist product to the cart. It captures the displayed current price, excluding the old-price span, and compares it with the cart price. checkCart verifies one row, quantity one and totals. Reload must preserve the cart, and its link must open the correct product. Limitation: local let declarations shadow the outer wishlist/cart variables, so the afterEach cleanup hooks currently return without cleanup. The presentation does not claim cleanup succeeds. Sources: tests/wishlistToCart.spec.js; POM/wishlistToCart.page.js; tests/support/cartVerification.js.

## 11. Product Reviews

TC-008 creates a review summary containing a UUID, selects each configured rating and submits the form. After revisiting the same product URL it checks exactly one review with that summary, the reviewer name and review text. Submission-response checks and review-identifier attachments are commented out. The test suite implements no review-deletion operation, so submitted reviews remain. Sources: tests/productReview.spec.js; POM/productReview.page.js.

## 12. Billing & Profile Updates

The billing scenario uses the chromium-authenticated project and checks updated billing values after reload. The profile scenario uses a unique-account fixture and checks name/contact after reload and re-login, then restores the original values. These tests do not imply all application data is cleaned up. Sources: tests/updateBillingAddress.spec.js; tests/updateProfile.spec.js; POM/updateBillling.page.js; POM/updateProfile.page.js; playwright.config.js.

## 13. Password Change Validation

This is an incorrect-current-password rejection scenario, not successful password-change coverage. The test signs in with the configured existing account, submits an invalid current password with a proposed new password, checks the configured error dialog, logs out and verifies that login with the original password still works. Sources: tests/changePassword.spec.js; POM/changePassword.page.js; testData/testData.json.

## 14. Checkout & Pending Payments

The paymentPending scenario reuses shared saved authentication. It adds a book, proceeds to checkout without submitting payment, and opens the pending-payments view. The assertion checks the expected URL and a matching product heading. It can match an older entry and does not uniquely correlate the newly created order. Sources: tests/paymentPending.spec.js; POM/myAccount.page.js; playwright.config.js.

## 15. Purchase & Order Tracking

The purchase test creates a unique account, signs in, adds one product from each of Books, Fashion, Furniture and Electronics, sets billing and shipping fields, reapplies billing as a workaround documented in the source, and submits the internet-banking option. It asserts the configured tracking-link count, captures each popup and logs out. It does not verify external payment settlement or assert each order status. The image is an existing repository artifact, screenshots/track-order-1.png; it shows Order Not Process Yet and is not evidence of a new run. Sources: tests/purchaseAndTrackOrder.spec.js; POM/trackproduct.page.js; screenshots/track-order-1.png.

## 16. Functional Dependencies

Six specs import shopping.fixture: repeatedAddToCart, wishlistPersistence, wishlistToCart, productReview, updateProfile and loginLogout. Two specs use saved authentication: paymentPending and updateBillingAddress. Three remaining specs arrange their own starting state: searchProduct, purchaseAndTrackOrder and changePassword. The shared-state project depends on setup and a saved session file. The fixture performs session teardown but does not delete generated accounts. Sources: tests imports; tests/support/shopping.fixture.js; tests/auth.setup.js; playwright.config.js.

## 17. Business Workflows

This slide provides two concise demonstration paths directly connected to source scenarios. The wishlist-to-cart path should show persistence, item identity and the reusable cart assertion helper. The login/logout path should show the identity check followed by signed-out assertions. These are implemented test expectations, not fresh execution results. Sources: tests/wishlistToCart.spec.js; tests/loginLogout.spec.js; tests/support/cartVerification.js.

## 18. Execution & Reporting

BASE_URL must be present in .env or the process environment and must use HTTP or HTTPS. The three active projects are setup, chromium-authenticated and chromium. workers is one. Retries are two when CI is truthy and zero locally. The global reporter is HTML and trace is on-first-retry. Six fixture specs override diagnostics to screenshot only-on-failure and trace retain-on-failure. No fresh suite run was performed for preparing this deck. An existing .last-run.json reports failed, but it is insufficient to compute a complete suite pass rate. Sources: playwright.config.js; tests/*.spec.js; test-results/.last-run.json.

## 19. CI & Delivery Workflow

Jenkinsfile uses agent any but runs bat commands, so it requires a Windows-capable agent. BASE_URL is injected through the Project_BaseURL credential. The pipeline installs dependencies and browsers, runs tests, and publishes the HTML report when present. It does not explicitly set CI. GitHub Actions runs on Ubuntu for pushes/pull requests to main/master, uses npm ci and uploads the report with 30-day retention. It currently does not inject the required BASE_URL. The files establish intended CI behavior, not a successful run. Sources: Jenkinsfile; .github/workflows/playwright.yml; playwright.config.js.

## 20. Coverage & Next Improvements

Coverage totals are based on 11 business tests in 11 spec files. Shopping and discovery: search, repeated cart, wishlist persistence, wishlist to cart, product reviews (5). Account management: login/logout, profile update, incorrect-password rejection, billing update (4). Checkout and orders: purchase/tracking and pending payments (2). The sample reference had an effort table, but this repository provides no approved estimates, so the deck uses verified inventory and future priorities. Improvement priorities include fixing shadowed cleanup references in wishlistToCart and wishlistPersistence, stronger exact-order assertions, account/review cleanup, environment configuration and enabling additional browsers. No pass rate or time saving is claimed.

## 21. Thank You

Close by emphasizing the separation of tests, page objects, fixtures and JSON data. The repository covers eleven business scenarios with checks for calculations, persistence and session behavior. Suggested discussion topics are the POM design, authentication trade-offs, CI configuration and stronger future assertions. Sources for slide facts are included throughout the speaker notes.