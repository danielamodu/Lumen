from dataclasses import dataclass
from typing import Optional


@dataclass
class BriefResult:
    warning: Optional[str]
    pattern: Optional[str]
    cross_domain: Optional[str]
    confidence: str
    raw_outcomes: int


@dataclass
class RecordResult:
    status: str
    message: str
