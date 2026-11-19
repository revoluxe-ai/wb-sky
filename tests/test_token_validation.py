"""Synthetic Wildberries JWT validation tests: no customer-issued tokens."""

from __future__ import annotations

import datetime

import jwt
import pytest

from app.modules.common_slaves.wildberries.models import WBToken

pytestmark = pytest.mark.unit


def _test_token(*, category_bits: int = 1 << 5, hours_until_expiry: int = 24) -> str:
    """Make a JWT fixture from test-only claims; not a real WB credential."""
    expiry = datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=hours_until_expiry)
    payload = {
        "sid": "123e4567-e89b-42d3-a456-426614174000",
        "uid": 123456,
        "s": category_bits,
        "exp": int(expiry.timestamp()),
    }
    return jwt.encode(payload, "synthetic-test-signing-key", algorithm="HS256")


TOKENS = [
    (_test_token(), True),
    (_test_token(category_bits=(1 << 5) | (1 << 30)), False),
    (_test_token(hours_until_expiry=-1), False),
    (_test_token(category_bits=(1 << 2)), False),
]


@pytest.mark.parametrize("token, expected", TOKENS)
def test_token_validity_simple(token: str, expected: bool) -> None:
    """Personal JWT syntax, expiry and Statistics permission decisions."""
    t = WBToken(api_key=token)
    is_valid = (
        t.check_valid()
        and (not t.read_only)
        and (not t.is_expired)
        and ("Статистика" in t.categories)
    )
    assert is_valid == expected
