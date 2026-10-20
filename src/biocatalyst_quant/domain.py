"""Small, typed, side-effect-free financial domain primitives."""

from dataclasses import dataclass
from datetime import datetime
from math import isfinite


@dataclass(frozen=True, slots=True)
class HistoricalFeature:
    """Feature and earliest time the strategy is permitted to observe it."""

    name: str
    value: float
    available_at: datetime
    source_id: str

    def __post_init__(self) -> None:
        if self.available_at.tzinfo is None or self.available_at.utcoffset() is None:
            raise ValueError("available_at must be timezone-aware")
        if not isfinite(self.value):
            raise ValueError("feature values must be finite")
        if not self.source_id:
            raise ValueError("source_id must not be empty")


def is_available(feature: HistoricalFeature, decision_at: datetime) -> bool:
    """Permit a feature only when its evidence was available by decision time."""
    if decision_at.tzinfo is None or decision_at.utcoffset() is None:
        raise ValueError("decision_at must be timezone-aware")
    return feature.available_at <= decision_at


def equal_weight_return(returns: tuple[float, ...]) -> float:
    """One-period, equal-initial-dollar-weight return before costs."""
    if len(returns) != 10:
        raise ValueError("exactly 10 stock returns are required")
    if any(not isfinite(value) or value < -1 for value in returns):
        raise ValueError("returns must be finite and cannot be below -100%")
    return sum(returns) / len(returns)
