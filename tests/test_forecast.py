"""A 04-es jegy előrejelző modelljének tesztjei (07-es jegy).

Futtatás a projekt gyökeréből:  python -m pytest
"""

import numpy as np
import pandas as pd
import pytest

from forecast import MIN_POINTS, NotEnoughData, make_forecast


def sample_closes(n=120, start=100.0, daily_growth=0.002, seed=1, tz=None):
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2026-05-01", periods=n, tz=tz)
    prices = start * np.exp(np.cumsum(daily_growth + rng.normal(0, 0.01, n)))
    return pd.Series(prices, index=dates)


@pytest.mark.parametrize("horizon", [7, 30])
def test_length_and_weekdays(horizon):
    closes = sample_closes()
    points = make_forecast(closes, horizon)["points"]
    assert len(points) == horizon
    dates = pd.to_datetime([p["date"] for p in points])
    assert dates[0] > closes.index[-1]
    assert all(d.weekday() < 5 for d in dates)  # csak hétköznapok


def test_band_contains_value_and_widens():
    points = make_forecast(sample_closes(), 30)["points"]
    assert all(p["lower"] < p["value"] < p["upper"] for p in points)
    assert points[-1]["upper"] - points[-1]["lower"] > points[0]["upper"] - points[0]["lower"]


def test_rising_trend_is_detected():
    rising = pd.Series(100 * np.exp(0.01 * np.arange(80)),
                       index=pd.bdate_range("2026-01-01", periods=80))
    result = make_forecast(rising, 7)
    assert result["model"]["daily_trend_pct"] == pytest.approx(1.005, abs=0.01)
    assert result["points"][-1]["value"] > float(rising.iloc[-1])


def test_falling_trend_is_detected():
    falling = pd.Series(100 * np.exp(-0.01 * np.arange(80)),
                        index=pd.bdate_range("2026-01-01", periods=80))
    assert make_forecast(falling, 7)["points"][-1]["value"] < float(falling.iloc[-1])


def test_starts_from_last_real_price():
    closes = sample_closes()
    first = make_forecast(closes, 7)["points"][0]["value"]
    assert first == pytest.approx(float(closes.iloc[-1]), rel=0.02)


def test_timezone_aware_index_like_yfinance():
    # a yfinance időzónás dátumokat ad vissza (pl. America/New_York)
    points = make_forecast(sample_closes(tz="America/New_York"), 7)["points"]
    assert len(points) == 7


def test_missing_and_bad_values_are_ignored():
    closes = sample_closes()
    closes.iloc[5] = np.nan
    closes.iloc[6] = 0
    assert len(make_forecast(closes, 7)["points"]) == 7


def test_too_few_points_raises():
    with pytest.raises(NotEnoughData):
        make_forecast(sample_closes(n=MIN_POINTS - 1), 7)
