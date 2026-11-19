# Kubernetes manifests (open-source candidate)

Only generic, reviewed examples and migration SQL are retained in this candidate.
Production deployments, cluster troubleshooting scripts, live topology and internal access runbooks are intentionally excluded.

- `migrations/sql/`: application database migration-control SQL.
- `monitoring/setup-telegram-alerts.sh`: generic, opt-in Telegram Alertmanager setup. Requires an explicit CHAT_ID and preconfigured Kubernetes secret; does not contain live credentials.

This directory is **not** a ready-to-deploy production stack.
