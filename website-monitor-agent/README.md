# Website Monitor Agent (Free)

Automated monitoring every 20 minutes using GitHub Actions.

## Flow
1. Check Website A.
2. If A is up, stop (no email).
3. If A is down, check Website B.
4. If B is down, email an alert immediately. **Do not check A again in this cycle.**
5. If B is up, check Website A one more time.
6. If A is now up, stop without email.
7. If A remains down, email an alert.

## Required GitHub Actions secrets
Add these repository secrets under **Settings → Secrets and variables → Actions → New repository secret**:

- `WEBSITE_A_URL` — primary website URL (include https://)
- `WEBSITE_B_URL` — backup website URL (include https://)
- `SMTP_EMAIL` — Gmail address used to send alerts
- `SMTP_APP_PASSWORD` — Gmail App Password (not your regular Gmail password)
- `ALERT_TO_EMAIL` — destination email address for alerts

## Gmail setup
Use a Gmail account with 2-Step Verification enabled. Create a Gmail App Password and store it only as the `SMTP_APP_PASSWORD` secret. Never commit credentials.

## Run manually
GitHub Actions → Website Monitor Agent → Run workflow.

## Schedule note
The cron schedule is `*/20 * * * *` (every 20 minutes, UTC). GitHub Actions scheduled workflows are not guaranteed to start at the exact minute and may be delayed. This uses GitHub-hosted runners and is subject to the account's Actions limits.

## Failure criteria
HTTP status 200–399 is treated as healthy. HTTP errors, timeouts, DNS/network errors, or other exceptions are treated as failed checks.
