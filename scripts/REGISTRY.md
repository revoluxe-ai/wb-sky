# scripts/ readiness registry

Ledger for `/opsx-scripts` (daily) and `/opsx-scripts-prepare`.

Human display: `Title (path)` — see `.cursor/commands/opsx-human-label-display.md`.

Do not set `battle_tested=YES` without Owner `RECORD_BATTLE GO` + evidence.

## Schema

| title | path | runnable | tests | battle_tested | last_local_at | last_cluster_at | last_image_ref | notes |
|-------|------|----------|-------|---------------|----------------|-----------------|----------------|-------|
| short human name | `scripts/<entrypoint>` | `UNKNOWN` \| `WORKS` \| `BROKEN` | `NONE` \| `PARTIAL` \| `COVERED` | `NO` \| `YES` | ISO UTC or `-` | ISO UTC or `-` | image ref or `-` | short |

## Entrypoints

| title | path | runnable | tests | battle_tested | last_local_at | last_cluster_at | last_image_ref | notes |
|-------|------|----------|-------|---------------|----------------|-----------------|----------------|-------|
| Adv-bot historical state extractor | scripts/adv_bot_historical_state_extractor.py | WORKS | COVERED | NO | 2026-08-25T21:44:04Z | 2026-08-25T22:40:00Z | [private-image-redacted] | Legacy ledger row; not available to resolver. |
| Backfill L2 | scripts/backfill_l2.py | UNKNOWN | NONE | NO | - | - | - | Legacy ledger row; not available to resolver. |
| Backfill MV for keyword clusters | scripts/backfill_mv_for_keyword_clusters.py | UNKNOWN | NONE | NO | - | - | - | Legacy ledger row; not available to resolver. |
| Delete user by Telegram id | scripts/delete_user_by_telegram_id.py | UNKNOWN | NONE | NO | - | - | - | Legacy ledger row; not available to resolver. |
| Enable individual keywords for new tariff cabinets | scripts/enable_individual_keywords_for_new_tariff_cabinets.py | UNKNOWN | NONE | NO | - | - | - | Legacy ledger row; not available to resolver. |
| Export last WB movements | scripts/export_last_wb_movements.py | UNKNOWN | NONE | NO | - | - | - | Legacy ledger row; not available to resolver. |
| Export non-zero balance users | scripts/export_non_zero_balance_users.py | UNKNOWN | NONE | NO | - | - | - | Legacy ledger row; not available to resolver. |
| Export single-article campaign stats | scripts/export_single_article_campaigns_stats.py | UNKNOWN | NONE | NO | - | - | - | Legacy ledger row; not available to resolver. |
| Fill bid decision | scripts/fill_bid_decision.py | UNKNOWN | NONE | NO | - | - | - | Legacy ledger row; not available to resolver. |
| Get dialogs from TG export | scripts/get_dialogs_from_tg_export.py | UNKNOWN | NONE | NO | - | - | - | Legacy ledger row; not available to resolver. |
| Get users | scripts/get_users/get_users.py | UNKNOWN | NONE | NO | - | - | - | Legacy ledger row; not available to resolver. |
| Get users for shop (worst adv) | scripts/get_worst_adv/get_users_for_shop_id.py | UNKNOWN | NONE | NO | - | - | - | Legacy ledger row; not available to resolver. |
| Insert adv deltas | scripts/insert_adv_deltas.py | UNKNOWN | NONE | NO | - | - | - | Legacy ledger row; not available to resolver. |
| Main user generator | scripts/users_communicate_module/main_user_generator.py | UNKNOWN | NONE | NO | - | - | - | Legacy ledger row; not available to resolver. |
| Migrate black phrases Redis to Postgres | scripts/migrate_black_phrases_redis_to_postgres.py | UNKNOWN | NONE | NO | - | - | - | Legacy ledger row; not available to resolver. |
| Path smoke | scripts/test_path.py | UNKNOWN | NONE | NO | - | - | - | Legacy ledger row; not available to resolver. |
| Resource gap | scripts/resource_gap.py | UNKNOWN | NONE | NO | - | - | - | Legacy ledger row; not available to resolver. |
| Billing debug cabinet | scripts/run_billing_debug_cabinet.py | UNKNOWN | NONE | NO | - | - | - | Legacy ledger row; not available to resolver. |
| Send message to all users | scripts/send_message/send_message_all_users.py | UNKNOWN | NONE | NO | - | - | - | Legacy ledger row; not available to resolver. |
| Send single messages | scripts/send_message/single_messages.py | UNKNOWN | NONE | NO | - | - | - | Legacy ledger row; not available to resolver. |
| Set false for non-qualifying users | scripts/set_false_for_non_qualifying_users.py | UNKNOWN | NONE | NO | - | - | - | Legacy ledger row; not available to resolver. |
| Set old user passed gate | scripts/set_old_user_passed_gate.py | UNKNOWN | NONE | NO | - | - | - | Legacy ledger row; not available to resolver. |
| Set relevant if white phrase | scripts/set_relevant_if_white_phrase.py | UNKNOWN | NONE | NO | - | - | - | Legacy ledger row; not available to resolver. |
| Set sales plan | scripts/set_sales_plan.py | UNKNOWN | NONE | NO | - | - | - | Legacy ledger row; not available to resolver. |
| Set shop id for all WB tokens | scripts/set_shop_id_for_all_wbtokens.py | UNKNOWN | NONE | NO | - | - | - | Legacy ledger row; not available to resolver. |
| Start campaigns by nmids | scripts/start_campaigns_by_nmids.py | UNKNOWN | NONE | NO | - | - | - | Legacy ledger row; not available to resolver. |
| Strict single-NMID read-only audit | scripts/strict_single_nmid_audit.py | UNKNOWN | COVERED | NO | - | - | - | Generic identity-safe bounded audit; readers are injected by Owner-bot Job. |
| Translit YAML | scripts/translit_yaml.py | UNKNOWN | NONE | NO | - | - | - | Legacy ledger row; not available to resolver. |
| Users CSV export | scripts/users_csv_exporter/csv_export.py | WORKS | NONE | NO | - | 2026-08-14T12:47:00Z | [private-image-redacted] | Legacy ledger row; not available to resolver. |
| WB API read-only preflight/collect | scripts/wb_api_readonly_ops/run.py | WORKS | PARTIAL | NO | 2026-08-21T10:54:00Z | 2026-08-21T15:40:00Z | [private-image-redacted] | Legacy ledger row; not available to resolver. |

## Support (not Job entrypoints)

Tracked only as notes; not run via `ops-script-runner` unless Owner promotes:

* `scripts/set_path.py` — path bootstrap
* `scripts/template_script.py` — authoring template
* `scripts/__init__.py` and package `__init__.py` / helper modules under `send_message/utils`, `get_users/filters`, etc.

## Infra pointers

* Prepare: `/opsx-scripts-prepare`
* Operate: `/opsx-scripts`
* Display SoT: `.cursor/commands/opsx-human-label-display.md`
* Workflow: `.github/workflows/deploy_scripts.yml` (branch `scripts`, tag `scripts`; CI push GHCR only)
* Cluster Job image (Harbor proxy-cache pull-through): `[private-image-redacted]
* Job template: `k8s/jobs/ops-script-runner.yaml` (`__HOLD_SECONDS__` default 900)
