"""Egyszerű árfolyam-előrejelző modell (TR_04).

Módszer:
- az utolsó WINDOW kereskedési nap záróárának logaritmusára egyenest illesztünk
  (lineáris trend), ennek meredeksége a napi átlagos változás;
- a becslés az utolsó valós záróárból indul, és ezzel a napi trenddel halad tovább;
- a 95%-os sáv a napi loghozamok szórásából jön: ±1,96 · szórás · √k
  (k = hány kereskedési nappal vagyunk az utolsó valós adat után).

Ez szándékosan egyszerű, magyarázható modell egyetemi projekthez,
nem befektetési tanács.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

WINDOW = 60       # ennyi utolsó kereskedési napból számolunk trendet
MIN_POINTS = 30   # ennél kevesebb adatból nem készítünk becslést
Z_95 = 1.96       # 95%-os sávhoz tartozó szorzó


class NotEnoughData(ValueError):
    """Túl kevés érvényes adatpont az előrejelzéshez."""


def make_forecast(closes: pd.Series, horizon: int) -> dict:
    """Előrejelzés `horizon` kereskedési napra.

    `closes`: dátum szerint rendezett záróárak (index: dátum).
    Visszaad: {"points": [{date, value, lower, upper}, ...], "model": {...}}
    """
    s = closes.dropna()
    s = s[s > 0]
    if len(s) < MIN_POINTS:
        raise NotEnoughData(
            f"Legalább {MIN_POINTS} kereskedési nap adata kell, most csak {len(s)} van."
        )

    recent = s.iloc[-WINDOW:]
    log_prices = np.log(recent.to_numpy(dtype=float))
    x = np.arange(len(log_prices))
    slope, _intercept = np.polyfit(x, log_prices, 1)

    log_returns = np.diff(log_prices)
    sigma = float(np.std(log_returns, ddof=1))

    last_price = float(s.iloc[-1])
    last_date = pd.Timestamp(s.index[-1]).normalize()
    future_dates = pd.bdate_range(start=last_date + pd.offsets.BDay(1), periods=horizon)

    points = []
    for k, day in enumerate(future_dates, start=1):
        center = last_price * np.exp(slope * k)
        spread = Z_95 * sigma * np.sqrt(k)
        points.append(
            {
                "date": day.strftime("%Y-%m-%d"),
                "value": round(float(center), 4),
                "lower": round(float(center * np.exp(-spread)), 4),
                "upper": round(float(center * np.exp(spread)), 4),
            }
        )

    return {
        "points": points,
        "model": {
            "name": "Lineáris trend (log ár) + 95%-os sáv",
            "window_days": int(len(recent)),
            "daily_trend_pct": round(float(np.expm1(slope) * 100), 4),
            "daily_volatility_pct": round(sigma * 100, 4),
        },
    }
