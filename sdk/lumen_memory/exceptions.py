class LumenError(Exception):
    """Base exception for Lumen SDK errors."""
    pass


class LumenConnectionError(LumenError):
    """Cannot reach the Lumen API server."""
    pass


class LumenValidationError(LumenError):
    """Invalid input parameters."""
    pass


class LumenAPIError(LumenError):
    """API returned an error response."""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"API error {status_code}: {detail}")
