// @ts-check
const { defineConfig, devices } = require("@playwright/test");
const { loadEnvFile } = require("node:process");
const { existsSync } = require("node:fs");
const { join } = require("node:path");

const envPath = join(__dirname, ".env");
if (existsSync(envPath)) loadEnvFile(envPath);

if (!process.env.BASE_URL) {
  throw new Error("BASE_URL is required. Set it in .env or the environment.");
}
const baseURL = new URL(process.env.BASE_URL);
if (!["http:", "https:"].includes(baseURL.protocol)) {
  throw new Error("BASE_URL must use http or https.");
}
// Preserve the application subdirectory when resolving relative page paths.
if (!baseURL.pathname.endsWith("/")) baseURL.pathname += "/";

module.exports = defineConfig({
  testDir: './tests',
  /* Run tests in files in parallel */
  fullyParallel: true,
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  /* Opt out of parallel tests on CI. */
  workers: 1,
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: 'html',
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    baseURL: baseURL.href,
    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: 'on-first-retry',
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: 'setup',
      testMatch: /auth\.setup\.js/,
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'chromium-authenticated',
      testMatch: /(?:paymentPending|updateBillingAddress)\.spec\.js/,
      dependencies: ['setup'],
      use: {
        ...devices['Desktop Chrome'],
        storageState: join(__dirname, 'playwright/.auth/user.json'),
      },
    },
    {
      name: 'chromium',
      testIgnore: [ /auth\.setup\.js/, /(?:paymentPending|updateBillingAddress)\.spec\.js/ ],
      use: { ...devices['Desktop Chrome'] },
    },

    // {
    //   name: 'firefox',
    //   use: { ...devices['Desktop Firefox'] },
    // },

    // {
    //   name: 'webkit',
    //   use: { ...devices['Desktop Safari'] },
    // },

    /* Test against mobile viewports. */
    // {
    //   name: 'Mobile Chrome',
    //   use: { ...devices['Pixel 5'] },
    // },
    // {
    //   name: 'Mobile Safari',
    //   use: { ...devices['iPhone 12'] },
    // },

    /* Test against branded browsers. */
    // {
    //   name: 'Microsoft Edge',
    //   use: { ...devices['Desktop Edge'], channel: 'msedge' },
    // },
    // {
    //   name: 'Google Chrome',
    //   use: { ...devices['Desktop Chrome'], channel: 'chrome' },
    // },
  ],

  /* Run your local dev server before starting the tests */
  // webServer: {
  //   command: 'npm run start',
  //   url: 'http://localhost:3000',
  //   reuseExistingServer: !process.env.CI,
  // },
});
