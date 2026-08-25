from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CandleData:
    timestamp: Any
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0
