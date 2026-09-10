"""Security hardening utilities for Lumen API.

Covers:
- Sliding-window rate limiting
- Bot and scanner protection
- Security headers & HTTPS enforcement
- Input sanitization & SSRF protection
- HMAC signing for webhooks
- Credential hashing & constant-time validation
- File upload restrictions
"""

import hmac
import hashlib
import ipaddress
import logging
import os
import re
import secrets
import threading
import time
from collections import defaultdict
from typing import Optional, Set
from urllib.parse import urlparse
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# ---------------------------------------------------------------------------
# 1. Credential Hashing & Constant-time comparison
# ---------------------------------------------------------------------------

def hash_api_key(api_key: str) -> str:
    """Compute SHA-256 hash of API key for safe storage/lookup."""
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def hash_password(password: str, salt: Optional[str] = None) -> str:
    """Hash a password using PBKDF2-HMAC-SHA256 with 100,000 iterations."""
    if not salt:
        salt = os.urandom(16).hex()
    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    ).hex()
    return f"{salt}${hashed}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against stored salt$hash with constant-time check."""
    if not stored_hash or "$" not in stored_hash:
        return False
    salt, expected = stored_hash.split("$", 1)
    computed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    ).hex()
    return hmac.compare_digest(computed, expected)


def secure_compare(a: Optional[str], b: Optional[str]) -> bool:
    """Constant-time string comparison to prevent timing attacks."""
    if a is None or b is None:
        return False
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


# ---------------------------------------------------------------------------
# 2. Input Sanitization & Validation (XSS, SSRF, Injection)
# ---------------------------------------------------------------------------

DOMAIN_REGEX = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")
USER_ID_REGEX = re.compile(r"^[a-zA-Z0-9_.-]{1,64}$")
TX_HASH_REGEX = re.compile(r"^0x[a-fA-F0-9]{64}$")

BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),       # Loopback
    ipaddress.ip_network("10.0.0.0/8"),        # RFC 1918 Class A
    ipaddress.ip_network("172.16.0.0/12"),     # RFC 1918 Class B
    ipaddress.ip_network("192.168.0.0/16"),    # RFC 1918 Class C
    ipaddress.ip_network("169.254.0.0/16"),    # Link-local / Cloud Metadata (AWS 169.254.169.254)
    ipaddress.ip_network("::1/128"),           # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),          # IPv6 unique local
    ipaddress.ip_network("fe80::/10"),         # IPv6 link-local
]


def sanitize_text(text: str, max_length: int = 500) -> str:
    """Strip null bytes / control chars, neutralize the reserved journal
    delimiter, and enforce max length.

    Values are returned as raw (un-escaped) text: output encoding is the
    consumer's job (the UI escapes at render time). HTML-escaping here would
    double-encode text served over the JSON API (e.g. "Q&A" -> "Q&amp;A").
    The '|' delimiter used by the pipe-delimited COLD journal
    (LUMEN|user|domain|signal|action|SEP|outcome) is replaced with '/' so a
    free-text value containing a pipe cannot break field parsing or silently
    drop the outcome.
    """
    if not text:
        return ""
    # Remove null bytes and non-printable control characters (except newline, tab, carriage return)
    cleaned = "".join(ch for ch in text if ch in "\n\r\t" or (ord(ch) >= 32 and ord(ch) != 127))
    # Neutralize the journal field delimiter to prevent delimiter injection.
    cleaned = cleaned.replace("|", "/")
    return cleaned.strip()[:max_length]


def validate_domain_name(domain: str) -> str:
    """Validate domain string against strict whitelist pattern."""
    d = domain.strip().lower()
    if not DOMAIN_REGEX.match(d):
        raise ValueError("Domain must be 1-64 alphanumeric characters, hyphens, or underscores.")
    return d


def validate_user_identifier(user_id: str) -> str:
    """Validate user_id, forbidding colons to prevent tenant prefix spoofing."""
    u = user_id.strip()
    if ":" in u:
        raise ValueError("User ID cannot contain colons (reserved for tenant scoping).")
    if not USER_ID_REGEX.match(u):
        raise ValueError("User ID must be 1-64 alphanumeric characters, underscores, hyphens, or dots.")
    return u


def validate_callback_url(url: str, allow_local: bool = False) -> str:
    """Validate webhook callback URL and block SSRF attacks against internal network."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Callback URL must use http or https protocol.")
    if not parsed.netloc:
        raise ValueError("Invalid callback URL host.")
    
    hostname = parsed.hostname or ""
    if not allow_local:
        if hostname.lower() in ("localhost", "127.0.0.1", "::1", "metadata.google.internal"):
            raise ValueError("SSRF blocked: Localhost and cloud metadata URLs are forbidden.")
        
        parsed_ip = None
        try:
            parsed_ip = ipaddress.ip_address(hostname)
        except ValueError:
            # hostname is a domain name, which is allowed
            pass

        if parsed_ip is not None:
            for net in BLOCKED_IP_NETWORKS:
                if parsed_ip in net:
                    raise ValueError(f"SSRF blocked: Private and internal IP addresses ({parsed_ip}) are forbidden.")

    return url


# ---------------------------------------------------------------------------
# 3. Webhook HMAC-SHA256 Signing
# ---------------------------------------------------------------------------

_configured_webhook_secret = os.environ.get("LUMEN_WEBHOOK_SECRET")
if _configured_webhook_secret:
    DEFAULT_WEBHOOK_SECRET = _configured_webhook_secret
else:
    # No configured secret: use a strong ephemeral per-process secret so
    # signatures can never be forged from a publicly known constant. Receivers
    # that need to verify signatures across restarts/instances must set
    # LUMEN_WEBHOOK_SECRET.
    DEFAULT_WEBHOOK_SECRET = secrets.token_hex(32)
    logging.getLogger("lumen.security").warning(
        "LUMEN_WEBHOOK_SECRET is not set; using an ephemeral random secret. "
        "Set LUMEN_WEBHOOK_SECRET for stable, verifiable webhook signatures."
    )

def sign_webhook_payload(payload_bytes: bytes, secret: Optional[str] = None) -> str:
    """Generate HMAC-SHA256 signature for outgoing webhook payload."""
    key = (secret or DEFAULT_WEBHOOK_SECRET).encode("utf-8")
    signature = hmac.new(key, payload_bytes, hashlib.sha256).hexdigest()
    return f"sha256={signature}"


# ---------------------------------------------------------------------------
# 4. File Upload Restriction Utility
# ---------------------------------------------------------------------------

DANGEROUS_EXTENSIONS: Set[str] = {
    ".exe", ".sh", ".bat", ".cmd", ".com", ".msi", ".scr",
    ".pif", ".vbs", ".js", ".jar", ".py", ".php", ".pl",
    ".cgi", ".asp", ".aspx", ".jsp", ".ps1", ".elf", ".so", ".dll"
}

ALLOWED_EXTENSIONS: Set[str] = {".json", ".csv", ".txt", ".png", ".jpg", ".jpeg", ".svg"}

def validate_file_upload(filename: str, content: bytes, max_size_bytes: int = 2 * 1024 * 1024) -> bool:
    """Validate uploaded file against size and executable extension blacklist."""
    if len(content) > max_size_bytes:
        raise HTTPException(status_code=413, detail=f"File too large. Maximum size is {max_size_bytes // 1024} KB.")
    
    # Path traversal protection
    base_name = os.path.basename(filename)
    if not base_name or "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid or malicious file path.")
        
    _, ext = os.path.splitext(base_name.lower())
    if ext in DANGEROUS_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Executable or dangerous file extension '{ext}' is forbidden.")
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Extension '{ext}' not in allowed whitelist.")
        
    return True


# ---------------------------------------------------------------------------
# 5. Sliding Window Rate Limiter
# ---------------------------------------------------------------------------

class SlidingWindowRateLimiter:
    """Memory-efficient, thread-safe sliding window rate limiter per client key / IP."""

    def __init__(self, requests_per_minute: int = 120):
        self.requests_per_minute = requests_per_minute
        self.windows = defaultdict(list)
        self._lock = threading.Lock()
        self._last_cleanup = 0.0

    def _cleanup_locked(self, now: float, window_seconds: int) -> None:
        """Evict keys whose most recent hit is outside the window. Caller holds the lock."""
        cutoff = now - window_seconds
        stale = [k for k, hist in self.windows.items() if not hist or hist[-1] <= cutoff]
        for k in stale:
            del self.windows[k]
        self._last_cleanup = now

    def is_allowed(self, key: str, max_requests: Optional[int] = None, window_seconds: int = 60) -> tuple[bool, int, int]:
        """Check if request is allowed. Returns (allowed, remaining, retry_after)."""
        limit = max_requests or self.requests_per_minute
        now = time.time()
        window_start = now - window_seconds

        # Guard all shared-state access: sync handlers run in a threadpool, so
        # is_allowed can be entered concurrently for the same key.
        with self._lock:
            # Opportunistically evict stale keys so the dict cannot grow without
            # bound (each distinct client key would otherwise leak an entry).
            if now - self._last_cleanup > window_seconds:
                self._cleanup_locked(now, window_seconds)

            # Prune old timestamps in place (keeps the same list object).
            history = self.windows[key]
            history[:] = [t for t in history if t > window_start]

            current_count = len(history)
            if current_count >= limit:
                oldest = history[0]
                retry_after = max(1, int(oldest + window_seconds - now))
                return False, 0, retry_after

            history.append(now)
            remaining = limit - (current_count + 1)
            return True, remaining, 0


# Global rate limiter instances
global_rate_limiter = SlidingWindowRateLimiter(
    requests_per_minute=int(os.environ.get("LUMEN_RATE_LIMIT", 120))
)
sensitive_rate_limiter = SlidingWindowRateLimiter(requests_per_minute=20)


# ---------------------------------------------------------------------------
# 6. Bot and Malicious Scanner Detection
# ---------------------------------------------------------------------------

SCANNER_USER_AGENTS = re.compile(
    r"(sqlmap|nikto|masscan|wpscan|acunetix|dirbuster|nmap|zgrab|gobuster|censys|shodan|python-requests/2\.2[0-5]|zmeu|havij)",
    re.IGNORECASE
)

PROBE_PATHS = (
    "/.env", "/.git", "/wp-admin", "/wp-login", "/phpmyadmin",
    "/etc/passwd", "/shell", "/actuator", "/swagger-ui.html",
    "/admin/config", "/console/", "/telescope"
)


def detect_bot_or_scanner(request: Request) -> Optional[str]:
    """Return description if request matches known malicious automated scanners."""
    user_agent = request.headers.get("user-agent", "").strip()
    # An empty User-Agent is intentionally NOT blocked: health checks, uptime
    # monitors, and many legitimate API clients omit the header.
    if user_agent and SCANNER_USER_AGENTS.search(user_agent):
        return f"Blocked vulnerability scanner user agent: {user_agent[:40]}"
    
    path = request.url.path.lower()
    for probe in PROBE_PATHS:
        if path.startswith(probe) or probe in path:
            return f"Blocked unauthorized probe path: {probe}"
            
    return None


# ---------------------------------------------------------------------------
# 7. Complete Security Middleware (Headers, HTTPS, Rate Limiting, Bot Defense)
# ---------------------------------------------------------------------------

def _get_client_ip(request: Request) -> str:
    """Resolve the client IP for rate limiting / HTTPS checks without trusting
    spoofable X-Forwarded-For.

    By default the direct peer address (request.client.host) is used, which a
    client cannot forge. Only when LUMEN_TRUST_PROXY_DEPTH is set to N>0 (the
    number of trusted reverse proxies in front of the app, e.g. 1 on Railway)
    is X-Forwarded-For consulted, and then the client is taken as the Nth entry
    from the right — the value appended by the first trusted proxy — so
    attacker-supplied left-hand entries are ignored.
    """
    peer = request.client.host if request.client else "127.0.0.1"
    try:
        depth = int(os.environ.get("LUMEN_TRUST_PROXY_DEPTH", "0"))
    except ValueError:
        depth = 0
    if depth <= 0:
        return peer
    forwarded_for = request.headers.get("x-forwarded-for", "")
    parts = [p.strip() for p in forwarded_for.split(",") if p.strip()]
    if not parts:
        return peer
    idx = max(0, len(parts) - depth)
    return parts[idx]


class LumenSecurityMiddleware(BaseHTTPMiddleware):
    """Centralized security middleware enforcing headers, rate limits, bot blocks, and HTTPS."""

    async def dispatch(self, request: Request, call_next):
        client_ip = _get_client_ip(request)

        # 1. Force HTTPS check
        force_https = os.environ.get("LUMEN_FORCE_HTTPS", "true").lower() in ("true", "1", "yes")
        proto = request.headers.get("x-forwarded-proto", "https").lower()
        if force_https and proto == "http" and request.url.scheme == "http":
            if not client_ip.startswith("127.") and client_ip != "::1":
                https_url = str(request.url).replace("http://", "https://", 1)
                return JSONResponse(
                    status_code=301,
                    headers={"Location": https_url},
                    content={"detail": "HTTPS required."}
                )

        # 2. Bot & Probe Detection
        bot_reason = detect_bot_or_scanner(request)
        if bot_reason:
            return JSONResponse(
                status_code=403,
                content={"error": "access_denied", "detail": "Forbidden request profile."}
            )

        # 3. Rate Limiting
        rate_key = f"{client_ip}:{request.headers.get('x-lumen-key', 'anon')}"
        path = request.url.path

        # Sensitive endpoints have stricter limits
        is_sensitive = path in ("/record", "/wipe", "/seed", "/tenants/create", "/market/brief")
        limiter = sensitive_rate_limiter if is_sensitive else global_rate_limiter
        limit_val = 20 if is_sensitive else global_rate_limiter.requests_per_minute

        allowed, remaining, retry_after = limiter.is_allowed(rate_key, max_requests=limit_val)
        if not allowed:
            return JSONResponse(
                status_code=429,
                headers={"Retry-After": str(retry_after)},
                content={
                    "error": "rate_limit_exceeded",
                    "detail": f"Too many requests. Please try again in {retry_after} seconds."
                }
            )

        # Proceed with request
        response = await call_next(request)

        # 4. Enforce Security Headers
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "img-src 'self' data: https:; "
            "script-src 'self' 'unsafe-inline' https://code.iconify.design; "
            "style-src 'self' 'unsafe-inline'; "
            "connect-src 'self' https:; "
            "font-src 'self' data:; "
            "frame-ancestors 'none';"
        )

        # Set rate limit headers
        response.headers["X-RateLimit-Limit"] = str(limit_val)
        response.headers["X-RateLimit-Remaining"] = str(remaining)

        # Ensure cookie security if Set-Cookie is emitted
        if "set-cookie" in response.headers:
            cookie = response.headers["set-cookie"]
            if "secure" not in cookie.lower():
                cookie += "; Secure"
            if "httponly" not in cookie.lower():
                cookie += "; HttpOnly"
            if "samesite" not in cookie.lower():
                cookie += "; SameSite=Strict"
            response.headers["set-cookie"] = cookie

        return response
