# WB Sky

WB Sky is a Python 3.11 project for managing and automating Wildberries advertising.

## Branch model

- `master` — release branch. PRs to `master` should come from `stage` only.
- `stage` — integration branch. Changes should arrive via PRs from feature branches.
- GitHub repository rulesets are configured and verified separately during release.
  Verify the live rules in **Settings → Rules → Rulesets** before relying on protection.

## Local development

Install Python 3.11 and Poetry. Review `env.sample`, configure your own credentials
outside Git, then install dependencies with `poetry install`.
Do not connect tests or development instances to production credentials.

## Security and release limitations

This repository ships source code, **not** production secrets or live infrastructure
configuration. Automated source and history secret scans and a Python syntax check
are performed by the release bootstrap, but these do **not** constitute an exhaustive
security audit or certify that all integration tests pass.

## License

Apache License, Version 2.0. See [LICENSE](LICENSE).

## Operator identity configuration

No real owner or administrator Telegram user IDs are stored as defaults.
Set PRESENTATION_NOTIFY_TELEGRAM_ID to your own positive Telegram user ID before
starting maintenance_leads_bot.py; it fails closed without this setting.
Set EXTRA_ADMIN_TELEGRAM_IDS, SUPPORT_CHANNEL_ID, EXCLUDED_TELEGRAM_USER_IDS
and TEST_TELEGRAM_USER_IDS as applicable. IDs in tests are synthetic.
The source release does not include production credentials or validated integration tests.
