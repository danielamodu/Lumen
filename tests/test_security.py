"""Automated security tests for Lumen API hardening."""

import pytest
from fastapi.testclient import TestClient
from api.server import app
from api.security import (
    sanitize_text,
    validate_domain_name,
    validate_user_identifier,
    validate_callback_url,
    validate_file_upload,
    sign_webhook_payload,
    hash_api_key,
    secure_compare,
    hash_password,
    verify_password,
)
from api.auth import DEMO_KEY

client = TestClient(app)


def test_security_headers_present():
    """Verify all standard HTTP security headers are set on responses."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "default-src" in response.headers.get("Content-Security-Policy", "")
    assert "max-age=" in response.headers.get("Strict-Transport-Security", "")


def test_bot_and_scanner_protection():
    """Verify malicious scanner User-Agents and probe paths are blocked with 403."""
    # 1. Scanner User-Agent
    res_scanner = client.get("/health", headers={"User-Agent": "sqlmap/1.5#stable"})
    assert res_scanner.status_code == 403
    assert res_scanner.json().get("error") == "access_denied"

    # 2. Probe path /.env
    res_env = client.get("/.env", headers={"User-Agent": "Mozilla/5.0"})
    assert res_env.status_code == 403

    # 3. Probe path /wp-admin
    res_wp = client.get("/wp-admin/config.php", headers={"User-Agent": "Mozilla/5.0"})
    assert res_wp.status_code == 403


def test_block_field_tampering():
    """Verify extra payload fields are rejected with 422 Unprocessable Entity."""
    tampered_payload = {
        "user_id": "alex",
        "domain": "pitch",
        "action": "demo",
        "outcome": "win",
        "signal": 1,
        "is_admin": True,               # Tampered field
        "tenant_id": "admin",           # Tampered field
        "sql_override": "DROP TABLE"    # Tampered field
    }
    response = client.post(
        "/record",
        json=tampered_payload,
        headers={"X-Lumen-Key": DEMO_KEY}
    )
    assert response.status_code == 422
    assert "extra_forbidden" in str(response.json())


def test_signal_out_of_bounds_rejected():
    """Verify signal values outside {-1, 0, 1} are rejected with 422."""
    for bad_signal in [2, -2, 999, -999]:
        payload = {
            "user_id": "alex",
            "domain": "pitch",
            "action": "test",
            "outcome": "test",
            "signal": bad_signal
        }
        response = client.post(
            "/record",
            json=payload,
            headers={"X-Lumen-Key": DEMO_KEY}
        )
        assert response.status_code == 422


def test_user_id_colon_injection_blocked():
    """Verify colons in user_id are blocked to prevent tenant prefix spoofing."""
    bad_payload = {
        "user_id": "other_tenant:admin_user",
        "domain": "pitch",
        "context": "test"
    }
    response = client.post(
        "/brief",
        json=bad_payload,
        headers={"X-Lumen-Key": DEMO_KEY}
    )
    assert response.status_code == 422


def test_ssrf_webhook_protection():
    """Verify webhook registration blocks loopback and private IP ranges."""
    # 1. Localhost
    payload_local = {
        "user_id": "alex",
        "domain": "pitch",
        "callback_url": "http://localhost:8000/internal-admin",
        "threshold": 0.10
    }
    res_local = client.post(
        "/webhooks",
        json=payload_local,
        headers={"X-Lumen-Key": DEMO_KEY}
    )
    assert res_local.status_code == 422

    # 2. Cloud metadata IP (AWS/GCP 169.254.169.254)
    payload_meta = {
        "user_id": "alex",
        "domain": "pitch",
        "callback_url": "http://169.254.169.254/latest/meta-data/",
        "threshold": 0.10
    }
    res_meta = client.post(
        "/webhooks",
        json=payload_meta,
        headers={"X-Lumen-Key": DEMO_KEY}
    )
    assert res_meta.status_code == 422

    # 3. Private Class A RFC1918
    payload_private = {
        "user_id": "alex",
        "domain": "pitch",
        "callback_url": "http://10.0.0.1/steal",
        "threshold": 0.10
    }
    res_private = client.post(
        "/webhooks",
        json=payload_private,
        headers={"X-Lumen-Key": DEMO_KEY}
    )
    assert res_private.status_code == 422


def test_webhook_hmac_signature_generation():
    """Verify HMAC-SHA256 signature format for outgoing webhooks."""
    body = b'{"event":"pattern_shift","signal":1}'
    sig = sign_webhook_payload(body, secret="test_secret_123")
    assert sig.startswith("sha256=")
    assert len(sig) == 7 + 64  # 'sha256=' + 64 hex characters


def test_file_upload_restrictions():
    """Verify executable file extensions are rejected by upload validator."""
    from fastapi import HTTPException
    for bad_file in ["exploit.exe", "shell.sh", "malware.py", "script.js"]:
        with pytest.raises(HTTPException) as exc_info:
            validate_file_upload(bad_file, b"test content")
        assert exc_info.value.status_code == 400

    # Valid file passes
    assert validate_file_upload("data.json", b'{"key": "value"}') is True


def test_password_and_key_hashing():
    """Verify salted password hashing and SHA-256 API key hashing."""
    pwd = "super_secure_password_123!"
    hashed = hash_password(pwd)
    assert "$" in hashed
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrong_password", hashed) is False

    key = "lmn_secret_token_abc"
    key_hash = hash_api_key(key)
    assert len(key_hash) == 64
    assert secure_compare(key, "lmn_secret_token_abc") is True
    assert secure_compare(key, "wrong_token") is False
