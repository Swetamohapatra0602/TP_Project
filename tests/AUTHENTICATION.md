# Authentication setup

Run the full suite with `npx.cmd playwright test`.

`auth.setup.js` signs in using `testData.user`, verifies the account, and saves
cookies and local storage to `playwright/.auth/user.json`. This file contains
session credentials and is excluded from Git.

The `chromium-authenticated` project depends on setup and loads that state for
`paymentPending.spec.js` and `updateBillingAddress.spec.js`. Each test receives
its own browser context, but both use the same server-side account. Keep the
configured single worker because these tests change shared account data.

Run only these tests with:

```powershell
npx.cmd playwright test --project=chromium-authenticated
```

Setup runs automatically and refreshes the state each time. Avoid `--no-deps`
unless you deliberately want to use an existing session.

The `chromium` project starts without saved authentication. Its tests create
their own accounts or exercise login, logout, and password behavior. Logging out
of a reused session can invalidate that session on the server, so those scenarios
must remain separate from the authenticated project.

To add another spec that reuses the saved session, include its filename in both
the authenticated project's `testMatch` and the regular project's `testIgnore`
in `playwright.config.js`, and omit its initial login steps.
