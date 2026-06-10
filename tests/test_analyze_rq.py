"""Tests for analyze_rq.py."""

import pandas as pd
import pytest

import analyze_rq


def test_rate_per_1000h():
    cells = pd.DataFrame({"n_hours": [500, 500], "n_accidents": [1, 2]})
    assert analyze_rq.rate_per_1000h(cells) == pytest.approx(3.0)


def test_rate_per_1000h_empty():
    cells = pd.DataFrame({"n_hours": [], "n_accidents": []})
    assert pd.isna(analyze_rq.rate_per_1000h(cells))


def test_rates_by_share_bins():
    cells = pd.DataFrame({
        "rain_share": [0.0, 0.1, 0.5],
        "n_hours": [1000, 1000, 1000],
        "n_accidents": [10, 20, 40],
    })
    rows = analyze_rq.rates_by_share(cells, "rain_share", "test")
    result = pd.DataFrame(rows, columns=["section", "group", "metric", "value"])
    rates = result[result["metric"] == "rate_per_1000h"].set_index("group")["value"]

    assert rates["none"] == pytest.approx(10.0)
    assert rates["low"] == pytest.approx(20.0)
    assert rates["high"] == pytest.approx(40.0)


def test_weather_ratios_on_synthetic_cells():
    # rainy cells have twice the accident rate of dry cells
    cells = pd.DataFrame({
        "rain_share": [0.0, 0.5] * 6,
        "frost_share": [0.0, 0.5] * 6,
        "month": [1, 1, 2, 2, 12, 12] * 2,
        "n_hours": [1000] * 12,
        "n_accidents": [10, 20] * 6,
    })
    rain_ratio, frost_ratio = analyze_rq.weather_ratios(cells)
    assert rain_ratio == pytest.approx(2.0)
    assert frost_ratio == pytest.approx(2.0)
