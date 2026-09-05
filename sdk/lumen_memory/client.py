"""Lumen Memory SDK client."""

import requests
from typing import Optional
from lumen_memory.types import BriefResult, RecordResult
from lumen_memory.exceptions import (
    LumenConnectionError,
    LumenValidationError, 
    LumenAPIError
)


class Lumen:
    """Client for the Lumen outcome memory API.
    
    Usage:
        lumen = Lumen(base_url="http://localhost:8000")
        lumen.record("alex", "pitch", "led with problem", 
                     "got meeting", 1)
        brief = lumen.brief("alex", "pitch", "about to pitch")
    """
    
    def __init__(
        self, 
        base_url: str = "https://lumen-memory-production.up.railway.app",
        api_key: str = "lmn_demo0000000000000000000000000000",
        timeout: int = 10
    ):
        """Initialize the Lumen client.
        
        Args:
            base_url: Base URL of the Lumen API server.
            api_key: Multi-tenant API key.
            timeout: Request timeout in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "lumen-memory-sdk/0.1.0",
            "X-Lumen-Key": api_key
        })
    
    def record(
        self,
        user_id: str,
        domain: str,
        action: str,
        outcome: str,
        signal: int
    ) -> RecordResult:
        """Record an outcome to Lumen memory.
        
        Args:
            user_id: Identifies the user.
            domain: Any string identifying the activity domain.
            action: What the user tried.
            outcome: What happened.
            signal: -1 (loss), 0 (neutral), or 1 (win).
            
        Returns:
            RecordResult with status and message.
            
        Raises:
            LumenValidationError: If signal is not -1, 0, or 1.
            LumenConnectionError: If the API server is unreachable.
            LumenAPIError: If the API returns an error response.
        """
        if signal not in (-1, 0, 1):
            raise LumenValidationError(
                f"Signal must be -1, 0, or 1. Got: {signal}"
            )
        if not user_id or not user_id.strip():
            raise LumenValidationError("user_id must be non-empty.")
        if not domain or not domain.strip():
            raise LumenValidationError("domain must be non-empty.")
            
        payload = {
            "user_id": user_id,
            "domain": domain,
            "action": action,
            "outcome": outcome,
            "signal": signal
        }
        
        response = self._post("/record", payload)
        return RecordResult(
            status=response["status"],
            message=response["message"]
        )
    
    def brief(
        self,
        user_id: str,
        domain: str,
        context: str = ""
    ) -> BriefResult:
        """Get a memory brief for a user and domain.
        
        Args:
            user_id: Identifies the user.
            domain: The activity domain to query.
            context: Optional context about current session.
            
        Returns:
            BriefResult with warning, pattern, cross_domain,
            confidence, and raw_outcomes.
            
        Raises:
            LumenConnectionError: If the API server is unreachable.
            LumenAPIError: If the API returns an error response.
        """
        payload = {
            "user_id": user_id,
            "domain": domain,
            "context": context
        }
        
        response = self._post("/brief", payload)
        return BriefResult(
            warning=response.get("warning"),
            pattern=response.get("pattern"),
            cross_domain=response.get("cross_domain"),
            confidence=response.get("confidence", ""),
            raw_outcomes=response.get("raw_outcomes", 0)
        )
    
    def seed(self) -> dict:
        """Seed the demo dataset. Used for testing only."""
        return self._post("/seed", {})
    
    def wipe(self) -> dict:
        """Wipe all memory. Used for testing only."""
        return self._post("/wipe", {})
    
    def _post(self, endpoint: str, payload: dict) -> dict:
        """Make a POST request to the Lumen API.
        
        Args:
            endpoint: API endpoint path (e.g. "/brief")
            payload: Request body dict.
            
        Returns:
            Parsed JSON response dict.
            
        Raises:
            LumenConnectionError: If server is unreachable.
            LumenAPIError: If server returns error status.
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.post(
                url,
                json=payload,
                timeout=self.timeout
            )
        except requests.exceptions.ConnectionError:
            raise LumenConnectionError(
                f"Cannot reach Lumen API at {self.base_url}. "
                f"Is the server running? "
                f"Start it with: python api/server.py"
            )
        except requests.exceptions.Timeout:
            raise LumenConnectionError(
                f"Request to {url} timed out after "
                f"{self.timeout}s."
            )
            
        if response.status_code >= 400:
            try:
                detail = response.json().get("detail", 
                                             response.text)
            except Exception:
                detail = response.text
            raise LumenAPIError(response.status_code, detail)
            
        return response.json()

    def register_webhook(
        self,
        user_id: str,
        domain: str,
        callback_url: str,
        threshold: float = 0.10
    ) -> dict:
        """Register a webhook for pattern shift notifications.
        
        Args:
            user_id: The user to watch.
            domain: The domain to watch.
            callback_url: URL to POST when pattern shifts.
            threshold: Minimum shift to trigger (default 0.10).
            
        Returns:
            Webhook dict including id for later deletion.
        """
        return self._post("/webhooks", {
            "user_id": user_id,
            "domain": domain,
            "callback_url": callback_url,
            "threshold": threshold
        })

    def list_webhooks(
        self,
        user_id: str = "alex",
        domain: str = None
    ) -> dict:
        """List registered webhooks."""
        params = f"?user_id={user_id}"
        if domain:
            params += f"&domain={domain}"
        return self._get(f"/webhooks{params}")

    def delete_webhook(self, webhook_id: str) -> dict:
        """Delete a webhook by ID."""
        return self._delete(f"/webhooks/{webhook_id}")

    def _get(self, endpoint: str) -> dict:
        """Make a GET request to the Lumen API."""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(
                url, timeout=self.timeout
            )
        except requests.exceptions.ConnectionError:
            raise LumenConnectionError(
                f"Cannot reach Lumen API at {self.base_url}."
            )
        except requests.exceptions.Timeout:
            raise LumenConnectionError(
                f"Request to {url} timed out after {self.timeout}s."
            )
        if response.status_code >= 400:
            try:
                detail = response.json().get(
                    "detail", response.text
                )
            except Exception:
                detail = response.text
            raise LumenAPIError(response.status_code, detail)
        return response.json()

    def _delete(self, endpoint: str) -> dict:
        """Make a DELETE request to the Lumen API."""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.delete(
                url, timeout=self.timeout
            )
        except requests.exceptions.ConnectionError:
            raise LumenConnectionError(
                f"Cannot reach Lumen API at {self.base_url}."
            )
        except requests.exceptions.Timeout:
            raise LumenConnectionError(
                f"Request to {url} timed out after {self.timeout}s."
            )
        if response.status_code >= 400:
            try:
                detail = response.json().get(
                    "detail", response.text
                )
            except Exception:
                detail = response.text
            raise LumenAPIError(response.status_code, detail)
        return response.json()

    def market_brief(
        self,
        domain: str,
        context: str = "",
        payment_proof: str = "demo_payment_proof_base_usdc"
    ) -> dict:
        """Query aggregate patterns across all users.
        
        For real payment:
        1. Send 0.01 USDC on Base mainnet to:
           0xf827fffabd004e81fdf0531b7ced3772452e52f0
        2. Pass the tx hash as payment_proof
        
        For demo:
        Use default payment_proof value.
        
        Args:
            domain: Domain to query.
            context: Optional context.
            payment_proof: Tx hash or demo proof string.
        """
        self.session.headers["X-Payment-Proof"] = (
            payment_proof
        )
        try:
            result = self._post("/market/brief", {
                "domain": domain,
                "context": context
            })
        finally:
            self.session.headers.pop(
                "X-Payment-Proof", None
            )
        return result

    def market_domains(self) -> dict:
        """List domains with market data available."""
        return self._get("/market/domains")
