"""Unit tests for adv_bot_historical_state_extractor helpers."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.adv_bot_historical_state_extractor import (
    ShopResolution,
    ShopResolutionError,
    assert_read_only_query,
    derive_effective_intervals,
    export_prod_revision_timeline,
    load_deployment_events,
    period_bounds,
    period_slug,
    primary_zip_name,
    resolve_shop_from_supplier_id,
    resolve_shop_identity,
    supplier_claims_from_api_key,
    try_git_revision_timeline,
)

SAMPLE_SHOP_FIXTURE_EVENTS = [
    {
        "deployed_at": "2026-08-01T00:00:00Z",
        "commit_sha": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "image_ref": "registry.example.invalid/example/wb-sky:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "image_digest": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
        "workflow_run_id": None,
        "evidence_source": "LAST.json+OPS_STATE.md",
        "evidence_ref": ".cursor/devops/LAST.json@111111111",
        "evidence_kind": "DIRECT_DEPLOYMENT_RECEIPT",
        "confidence": "MEDIUM",
        "notes": "OPS_STATE action log date only",
    },
    {
        "deployed_at": "2026-08-09T10:35:00Z",
        "commit_sha": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        "image_ref": "registry.example.invalid/example/wb-sky:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        "image_digest": "sha256:2222222222222222222222222222222222222222222222222222222222222222",
        "workflow_run_id": "10000000001",
        "evidence_source": "LAST.json",
        "evidence_ref": ".cursor/devops/LAST.json@222222222",
        "evidence_kind": "DIRECT_DEPLOYMENT_RECEIPT",
        "confidence": "HIGH",
        "notes": "",
    },
    {
        "deployed_at": "2026-08-10T05:58:00Z",
        "commit_sha": "cccccccccccccccccccccccccccccccccccccccc",
        "image_ref": "registry.example.invalid/example/wb-sky:cccccccccccccccccccccccccccccccccccccccc",
        "image_digest": "sha256:3333333333333333333333333333333333333333333333333333333333333333",
        "workflow_run_id": "10000000002",
        "evidence_source": "LAST.json",
        "evidence_ref": ".cursor/devops/LAST.json@333333333",
        "evidence_kind": "DIRECT_DEPLOYMENT_RECEIPT",
        "confidence": "HIGH",
        "notes": "",
    },
    {
        "deployed_at": "2026-08-14T09:05:00Z",
        "commit_sha": "dddddddddddddddddddddddddddddddddddddddd",
        "image_ref": "registry.example.invalid/example/wb-sky:dddddddddddddddddddddddddddddddddddddddd",
        "image_digest": "sha256:4444444444444444444444444444444444444444444444444444444444444444",
        "workflow_run_id": "10000000003",
        "evidence_source": "LAST.json+OPS_STATE.md",
        "evidence_ref": ".cursor/devops/LAST.json@444444444",
        "evidence_kind": "DIRECT_DEPLOYMENT_RECEIPT",
        "confidence": "HIGH",
        "notes": "",
    },
    {
        "deployed_at": "2026-08-16T10:50:00Z",
        "commit_sha": "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
        "image_ref": "registry.example.invalid/example/wb-sky:eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
        "image_digest": "sha256:5555555555555555555555555555555555555555555555555555555555555555",
        "workflow_run_id": "10000000004",
        "evidence_source": "LAST.json+OPS_STATE.md",
        "evidence_ref": ".cursor/devops/LAST.json@555555555",
        "evidence_kind": "DIRECT_DEPLOYMENT_RECEIPT",
        "confidence": "HIGH",
        "notes": "",
    },
]


def _write_fixture_ledger(path: Path, events: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(event) for event in events) + "\n",
        encoding="utf-8",
    )


@pytest.mark.unit
def test_primary_zip_name_sanitizes_case() -> None:
    name = primary_zip_name("OOO SAMPLE_SHOP", date(2026, 8, 6), date(2026, 8, 18))
    assert name == "ADV_BOT_INTERNAL_HISTORY_OOO_SAMPLE_SHOP_2026-08-06_2026-08-18.zip"


@pytest.mark.unit
def test_period_slug() -> None:
    assert period_slug(date(2026, 8, 6), date(2026, 8, 18)) == "2026-08-06_2026-08-18"


@pytest.mark.unit
def test_period_bounds_moscow() -> None:
    _, _, start, end = period_bounds(
        date(2026, 8, 6), date(2026, 8, 18), "Europe/Moscow"
    )
    assert start == "2026-08-06 00:00:00"
    assert end == "2026-08-18 23:59:59"


@pytest.mark.unit
def test_assert_read_only_query_blocks_insert() -> None:
    with pytest.raises(RuntimeError, match="Mutating SQL forbidden"):
        assert_read_only_query("INSERT INTO default_db.plan_fact_stats VALUES (1)")


@pytest.mark.unit
def test_assert_read_only_query_allows_select() -> None:
    assert_read_only_query("SELECT adv_id FROM default_db.plan_fact_stats WHERE adv_id = 1")


@pytest.mark.unit
def test_parse_args_requires_shop_or_supplier() -> None:
    from scripts.adv_bot_historical_state_extractor import parse_args

    with pytest.raises(SystemExit):
        parse_args(["--from", "2026-08-06", "--to", "2026-08-18"])

    args = parse_args(
        [
            "--supplier-id",
            "123456789",
            "--from",
            "2026-08-06",
            "--to",
            "2026-08-18",
        ]
    )
    assert args.supplier_id == "123456789"
    assert args.shop_id is None


@pytest.mark.unit
def test_parse_args_explicit_shop_id() -> None:
    from scripts.adv_bot_historical_state_extractor import parse_args

    args = parse_args(
        [
            "--shop-id",
            "123e4567-e89b-42d3-a456-426614174000",
            "--from",
            "2026-08-06",
            "--to",
            "2026-08-18",
            "--case",
            "SAMPLE_SHOP",
        ]
    )
    assert args.shop_id.startswith("123e")
    assert args.supplier_id is None


@pytest.mark.unit
def test_supplier_claims_from_api_key_uid() -> None:
    import jwt

    token = jwt.encode({"uid": 123456789, "sid": "shop-uuid"}, "secret", algorithm="HS256")
    claims = supplier_claims_from_api_key(token)
    assert "123456789" in claims


@pytest.mark.unit
def test_resolve_supplier_unique_wbcabinet_id(tmp_path: Path) -> None:
    sql_dir = tmp_path / "sql"
    sql_dir.mkdir()

    def fake_ephemeral(database: str, query: str, sql_dir: Path, name: str) -> list[dict]:
        if "wbcabinet" in query and "WHERE id" in query:
            return [{"shop_id": "resolved-shop-uuid"}]
        return []

    with patch(
        "scripts.adv_bot_historical_state_extractor._pg_query_ephemeral",
        side_effect=fake_ephemeral,
    ):
        resolution = resolve_shop_from_supplier_id("42", sql_dir)
    assert resolution.resolved_shop_id == "resolved-shop-uuid"
    assert resolution.shop_resolution_status == "RESOLVED"
    assert "wbcabinet.id" in resolution.shop_resolution_source


@pytest.mark.unit
def test_resolve_supplier_zero_matches_fail_closed(tmp_path: Path) -> None:
    sql_dir = tmp_path / "sql"
    sql_dir.mkdir()

    with patch(
        "scripts.adv_bot_historical_state_extractor._pg_query_ephemeral",
        return_value=[],
    ):
        with pytest.raises(ShopResolutionError, match="No shop_id"):
            resolve_shop_from_supplier_id("123456789", sql_dir)


@pytest.mark.unit
def test_resolve_supplier_ambiguous_fail_closed(tmp_path: Path) -> None:
    sql_dir = tmp_path / "sql"
    sql_dir.mkdir()
    import jwt

    token_a = jwt.encode({"uid": 123456789, "sid": "a"}, "s", algorithm="HS256")
    token_b = jwt.encode({"uid": 123456789, "sid": "b"}, "s", algorithm="HS256")

    def fake_ephemeral(database: str, query: str, sql_dir: Path, name: str) -> list[dict]:
        if "wbtoken" in query:
            return [
                {"shop_id": "shop-a", "api_key": token_a},
                {"shop_id": "shop-b", "api_key": token_b},
            ]
        return []

    with patch(
        "scripts.adv_bot_historical_state_extractor._pg_query_ephemeral",
        side_effect=fake_ephemeral,
    ):
        with pytest.raises(ShopResolutionError, match="Ambiguous"):
            resolve_shop_from_supplier_id("123456789", sql_dir)


@pytest.mark.unit
def test_resolve_explicit_shop_id(tmp_path: Path) -> None:
    sql_dir = tmp_path / "sql"
    sql_dir.mkdir()

    with patch(
        "scripts.adv_bot_historical_state_extractor._pg_query_ephemeral",
        return_value=[{"shop_id": "explicit-shop"}],
    ):
        resolution = resolve_shop_identity(
            supplier_id=None,
            shop_id="explicit-shop",
            sql_dir=sql_dir,
        )
    assert resolution.resolved_shop_id == "explicit-shop"
    assert resolution.shop_resolution_source == "explicit_shop_id"


@pytest.mark.unit
def test_manifest_provenance_fields() -> None:
    resolution = ShopResolution(
        requested_supplier_id="123456789",
        requested_shop_id=None,
        resolved_shop_id="uuid-here",
        shop_resolution_source="wbtoken.jwt_claim",
        shop_resolution_status="RESOLVED",
    )
    fields = resolution.manifest_fields()
    assert fields["requested_supplier_id"] == "123456789"
    assert fields["resolved_shop_id"] == "uuid-here"
    assert fields["shop_resolution_status"] == "RESOLVED"


@pytest.mark.unit
def test_load_deployment_events_reads_all_rows(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    _write_fixture_ledger(ledger, SAMPLE_SHOP_FIXTURE_EVENTS[:2])
    events = load_deployment_events(ledger_path=ledger)
    assert len(events) == 2
    assert events[0]["commit_sha"].startswith("fd6d2d")


@pytest.mark.unit
def test_derive_intervals_seeds_from_prior_deployment() -> None:
    intervals = derive_effective_intervals(
        SAMPLE_SHOP_FIXTURE_EVENTS,
        date(2026, 8, 6),
        date(2026, 8, 18),
        "Europe/Moscow",
    )
    assert intervals[0]["commit_sha"].startswith("fd6d2d")
    assert intervals[0]["evidence_kind"] == "INFERRED_CONTINUITY"
    assert intervals[0]["effective_from"].startswith("2026-08-06T00:00:00+03:00")


@pytest.mark.unit
def test_derive_intervals_closes_on_in_period_event() -> None:
    intervals = derive_effective_intervals(
        SAMPLE_SHOP_FIXTURE_EVENTS,
        date(2026, 8, 6),
        date(2026, 8, 18),
        "Europe/Moscow",
    )
    assert intervals[0]["effective_to"] == "2026-08-09T13:35:00+03:00"
    assert intervals[1]["effective_from"] == "2026-08-09T13:35:00+03:00"
    assert intervals[1]["evidence_kind"] == "DIRECT_DEPLOYMENT_RECEIPT"


@pytest.mark.unit
def test_derive_intervals_closes_final_interval_at_requested_to() -> None:
    intervals = derive_effective_intervals(
        SAMPLE_SHOP_FIXTURE_EVENTS,
        date(2026, 8, 6),
        date(2026, 8, 18),
        "Europe/Moscow",
    )
    assert intervals[-1]["commit_sha"].startswith("bb81f827")
    assert intervals[-1]["effective_to"] == "2026-08-18T23:59:59+03:00"


@pytest.mark.unit
def test_sample_shop_fixture_produces_five_expected_intervals() -> None:
    intervals = derive_effective_intervals(
        SAMPLE_SHOP_FIXTURE_EVENTS,
        date(2026, 8, 6),
        date(2026, 8, 18),
        "Europe/Moscow",
    )
    assert len(intervals) == 5
    assert [row["commit_sha"] for row in intervals] == [
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        "cccccccccccccccccccccccccccccccccccccccc",
        "dddddddddddddddddddddddddddddddddddddddd",
        "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
    ]
    assert intervals[0]["evidence_kind"] == "INFERRED_CONTINUITY"
    assert all(
        row["evidence_kind"] == "DIRECT_DEPLOYMENT_RECEIPT" for row in intervals[1:]
    )


@pytest.mark.unit
def test_empty_ledger_returns_not_available(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text("", encoding="utf-8")
    rows, meta = export_prod_revision_timeline(
        date(2026, 8, 6),
        date(2026, 8, 18),
        "Europe/Moscow",
        ledger_path=ledger,
    )
    assert rows == []
    assert meta["status"] == "NOT_AVAILABLE"
    assert meta["cluster_safe"] is False


@pytest.mark.unit
def test_period_after_all_deployments_returns_not_available(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    _write_fixture_ledger(ledger, SAMPLE_SHOP_FIXTURE_EVENTS[:1])
    rows, meta = export_prod_revision_timeline(
        date(2027, 1, 1),
        date(2027, 1, 2),
        "Europe/Moscow",
        ledger_path=ledger,
    )
    assert rows == []
    assert meta["status"] == "NOT_AVAILABLE"


@pytest.mark.unit
def test_committed_ledger_exports_intervals(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    _write_fixture_ledger(ledger, SAMPLE_SHOP_FIXTURE_EVENTS)
    rows, meta = export_prod_revision_timeline(
        date(2026, 8, 6),
        date(2026, 8, 18),
        "Europe/Moscow",
        ledger_path=ledger,
    )
    assert len(rows) == 5
    assert meta["status"] == "EXPORTED"
    assert meta["primary_source"] == "deployment_event_ledger"
    assert meta["cluster_safe"] is True


@pytest.mark.unit
def test_main_bootstraps_cluster_infra_before_shop_resolution() -> None:
    from scripts.adv_bot_historical_state_extractor import main

    call_order: list[str] = []

    def _bootstrap() -> None:
        call_order.append("bootstrap")

    def _resolve(**_kwargs: object) -> ShopResolution:
        call_order.append("resolve")
        return ShopResolution(
            requested_supplier_id="123456789",
            requested_shop_id=None,
            resolved_shop_id="shop-uuid",
            shop_resolution_source="wbtoken.jwt_claim",
            shop_resolution_status="RESOLVED",
        )

    with (
        patch(
            "scripts.adv_bot_historical_state_extractor.bootstrap_cluster_infra",
            side_effect=_bootstrap,
        ),
        patch(
            "scripts.adv_bot_historical_state_extractor.resolve_shop_identity",
            side_effect=_resolve,
        ),
        patch(
            "scripts.adv_bot_historical_state_extractor.run_collect",
            return_value={"EXECUTION_STATUS": "COMPLETE"},
        ),
    ):
        main(
            [
                "--supplier-id",
                "123456789",
                "--from",
                "2026-08-06",
                "--to",
                "2026-08-18",
            ]
        )
    assert call_order == ["bootstrap", "resolve"]


@pytest.mark.unit
def test_try_git_revision_timeline_no_git_binary(tmp_path: Path) -> None:
    with patch("scripts.adv_bot_historical_state_extractor.shutil.which", return_value=None):
        rows, errors = try_git_revision_timeline(
            date(2026, 8, 6), date(2026, 8, 18), "Europe/Moscow", repo_root=tmp_path
        )
    assert rows == []
    assert errors
