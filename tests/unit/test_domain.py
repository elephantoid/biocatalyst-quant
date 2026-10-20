from datetime import UTC, datetime, timedelta

import pytest

from biocatalyst_quant.domain import HistoricalFeature, equal_weight_return, is_available


def test_rejects_future_feature() -> None:
    now = datetime(2020, 1, 1, tzinfo=UTC)
    feature = HistoricalFeature("phase", 3.0, now + timedelta(seconds=1), "source-1")
    assert not is_available(feature, now)
    assert is_available(feature, now + timedelta(seconds=1))


def test_rejects_naive_timestamps() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        HistoricalFeature("phase", 3.0, datetime(2020, 1, 1), "source-1")


def test_equal_weight_return() -> None:
    returns = (1.0, 1.0, 1.0, -0.3, -0.3, -0.3, -0.3, -0.3, -0.3, -0.3)
    assert equal_weight_return(returns) == pytest.approx(0.09)


@pytest.mark.parametrize("count", [0, 5, 9, 11])
def test_requires_ten_stocks(count: int) -> None:
    with pytest.raises(ValueError, match="exactly 10"):
        equal_weight_return((0.0,) * count)


def test_rejects_non_finite_feature_value() -> None:
    with pytest.raises(ValueError, match="finite"):
        HistoricalFeature("phase", float("nan"), datetime(2020, 1, 1, tzinfo=UTC), "source-1")


def test_rejects_empty_source_id() -> None:
    with pytest.raises(ValueError, match="source_id"):
        HistoricalFeature("phase", 1.0, datetime(2020, 1, 1, tzinfo=UTC), "")


def test_rejects_naive_decision_time() -> None:
    feature = HistoricalFeature("phase", 3.0, datetime(2020, 1, 1, tzinfo=UTC), "source-1")
    with pytest.raises(ValueError, match="decision_at must be timezone-aware"):
        is_available(feature, datetime(2020, 1, 1))
