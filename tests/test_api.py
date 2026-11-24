"""Az /api/stock végpont tesztjei (07-es jegy). A Yahoo hívást mintaadatra cseréljük."""

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

import main


def fake_history(n):
    dates = pd.bdate_range(end="2026-11-20", periods=n, tz="America/New_York")
    prices = 150 * np.exp(np.cumsum(0.001 + np.random.default_rng(3).normal(0, 0.01, n)))
    return pd.DataFrame({"Close": prices}, index=dates)


class FakeTicker:
    def __init__(self, symbol, session=None):
        self.symbol = symbol

    def history(self, period="1mo", **kwargs):
        if self.symbol == "NINCSILYEN":
            return pd.DataFrame()
        if self.symbol == "KEVES":
            return fake_history(10)
        if self.symbol == "HIBA":
            raise ConnectionError("Yahoo nem elérhető")
        return fake_history(126)


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(main.yf, "Ticker", FakeTicker)
    main.get_cached_stock_data.cache_clear()
    yield TestClient(main.app)
    main.get_cached_stock_data.cache_clear()


def test_index_page(client):
    assert client.get("/").status_code == 200


@pytest.mark.parametrize("days", [7, 30])
def test_prediction_shape(client, days):
    data = client.get(f"/api/stock/aapl?days={days}").json()
    assert data["symbol"] == "AAPL"
    assert len(data["prices"]) == 10
    assert len(data["prediction"]) == days
    assert len(data["prediction_labels"]) == days
    assert len(data["prediction_lower"]) == days and len(data["prediction_upper"]) == days
    assert all(lo <= v <= up for lo, v, up in
               zip(data["prediction_lower"], data["prediction"], data["prediction_upper"]))


def test_prediction_is_not_fixed_percentage(client):
    # a korábbi változat fix +0,2%/nap volt; a modell a múltbeli adatokból számol
    data = client.get("/api/stock/AAPL?days=7").json()
    last = data["prices"][-1]
    old_style = [round(last * (1 + 0.002 * i), 2) for i in range(1, 8)]
    assert data["prediction"] != old_style
    assert "daily_trend_pct" in data["model"]


def test_invalid_days_400(client):
    assert client.get("/api/stock/AAPL?days=14").status_code == 400


def test_unknown_ticker_404(client):
    r = client.get("/api/stock/NINCSILYEN")
    assert r.status_code == 404
    assert "NINCSILYEN" in r.json()["detail"]


def test_not_enough_data_422(client):
    assert client.get("/api/stock/KEVES").status_code == 422


def test_data_source_error_500(client):
    r = client.get("/api/stock/HIBA")
    assert r.status_code == 500
    assert "Hiba történt" in r.json()["detail"]
