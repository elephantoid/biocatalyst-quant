"""Cross-component contract test using deterministic in-memory fixtures."""

from datetime import UTC, datetime, timedelta

import pytest

from biocatalyst_quant.domain import HistoricalFeature, equal_weight_return, is_available


@pytest.mark.integration
def test_only_predecision_features_reach_portfolio() -> None:
    decision_at = datetime(2020, 3, 10, 20, 0, tzinfo=UTC)
    old = HistoricalFeature("enrollment", 200.0, decision_at - timedelta(days=2), "doc-a")
    future = HistoricalFeature("endpoint_met", 1.0, decision_at + timedelta(days=1), "doc-b")
    eligible = [item for item in (old, future) if is_available(item, decision_at)]
    assert [item.name for item in eligible] == ["enrollment"]
    assert equal_weight_return((0.0,) * 10) == 0.0
