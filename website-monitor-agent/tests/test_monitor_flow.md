# Test scenarios

These are the expected outcomes to verify in workflow logs:

| Website A check 1 | Website B | Website A check 2 | Expected |
|---|---|---|---|
| Up | Not checked | Not checked | Stop; no email |
| Down | Up | Up | Stop; no email |
| Down | Up | Down | Send email |
| Down | Down | Not checked | Send email; **do not retry A** |

The live checks and email delivery are tested after the GitHub Actions secrets are configured.
