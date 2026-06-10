"""Analyse one research question and write a tidy result table.

The script reads the cell-level analysis table (weather exposure + accident
counts) and the accident table, runs the statistics for the selected research
question and writes a long-format CSV with the columns
section, group, metric, value.

Research questions:
    1 - precipitation/frost vs. accident frequency, severity and type
    2 - summer sun and heat vs. commuter-hour accident rates
    3 - weather sensitivity of the federal states
    4 - evolution of weather-related risk 2016-2024

Usage:
    python src/analyze_rq.py --rq 1 --table data/processed/analysis_table.csv \
        --accidents data/processed/accidents_stations.csv --output results/rq1_results.csv
"""

import argparse
import logging
import os
import sys

import pandas as pd
from scipy import stats

log = logging.getLogger("analyze_rq")

WINTER_MONTHS = [11, 12, 1, 2, 3]
SUMMER_MONTHS = [6, 7, 8]
CITY_STATES = ["Berlin", "Hamburg", "Bremen"]

ROAD_CONDITION_LABELS = {0: "dry", 1: "wet", 2: "icy"}


def rate_per_1000h(cells):
    """Accidents per 1000 station-hours over a set of cells."""
    hours = cells["n_hours"].sum()
    if hours == 0:
        return float("nan")
    return cells["n_accidents"].sum() / hours * 1000


def rates_by_share(cells, share_column, section):
    """Accident rates for cells binned by the share of e.g. rainy hours."""
    bins = {
        "none": cells[share_column] == 0,
        "low": (cells[share_column] > 0) & (cells[share_column] <= 0.15),
        "medium": (cells[share_column] > 0.15) & (cells[share_column] <= 0.35),
        "high": cells[share_column] > 0.35,
    }
    rows = []
    for label, mask in bins.items():
        subset = cells[mask]
        rows.append((section, label, "rate_per_1000h", rate_per_1000h(subset)))
        rows.append((section, label, "n_hours", subset["n_hours"].sum()))
        rows.append((section, label, "n_accidents", subset["n_accidents"].sum()))
    return rows


def analyze_rq1(cells, accidents):
    """Precipitation and frost vs. accident frequency, severity and type."""
    rows = rates_by_share(cells, "rain_share", "rate_by_rain_share")

    # light vs. heavy rain: compare cells that saw only light rain with
    # cells that saw at least some heavy rain
    dry = cells[cells["rain_share"] == 0]
    light = cells[(cells["rain_share"] > 0) & (cells["heavy_rain_share"] == 0)]
    heavy = cells[cells["heavy_rain_share"] > 0]
    for label, subset in [("dry", dry), ("light_rain", light), ("heavy_rain", heavy)]:
        rows.append(("rate_by_rain_intensity", label, "rate_per_1000h",
                     rate_per_1000h(subset)))

    # frost only compared within winter months to avoid seasonal bias
    winter = cells[cells["month"].isin(WINTER_MONTHS)]
    rows += rates_by_share(winter, "frost_share", "rate_by_frost_share_winter")

    # severity and accident type by road condition (directly from the accidents)
    table = pd.crosstab(accidents["road_condition"], accidents["severity"])
    chi2 = stats.chi2_contingency(table)
    for condition, label in ROAD_CONDITION_LABELS.items():
        subset = accidents[accidents["road_condition"] == condition]
        severe = (subset["severity"] <= 2).mean()
        loss = (subset["accident_type"] == 1).mean()
        rows.append(("severity_by_road_condition", label, "share_severe", severe))
        rows.append(("severity_by_road_condition", label, "n_accidents", len(subset)))
        rows.append(("type_by_road_condition", label, "share_loss_of_control", loss))
    rows.append(("severity_by_road_condition", "all", "chi2_p_value", chi2.pvalue))
    return rows


def analyze_rq2(cells, accidents):
    """Summer sun, heat and rain vs. commuter-hour accident rates."""
    # only stations with a solar radiation sensor can be used here
    commuter = cells[cells["month"].isin(SUMMER_MONTHS) & cells["is_commuter_hour"] &
                     cells["mean_solar"].notna()]

    groups = {
        "neutral": (commuter["strong_sun_share"] <= 0.5) &
                   (commuter["rain_share"] <= 0.15) &
                   (commuter["hot_share"] <= 0.5),
        "strong_sun": commuter["strong_sun_share"] > 0.5,
        "hot": commuter["hot_share"] > 0.5,
        "rainy": commuter["rain_share"] > 0.35,
    }
    rows = []
    baseline = rate_per_1000h(commuter[groups["neutral"]])
    for label, mask in groups.items():
        subset = commuter[mask]
        rate = rate_per_1000h(subset)
        rows.append(("commuter_rate_by_condition", label, "rate_per_1000h", rate))
        rows.append(("commuter_rate_by_condition", label, "n_hours",
                     subset["n_hours"].sum()))
        rows.append(("commuter_rate_by_condition", label, "rate_ratio_vs_neutral",
                     rate / baseline))

    # correlation between solar radiation and the accident rate across
    # station-months (commuter hours only)
    monthly = commuter.groupby(["station_id", "year", "month"]).agg(
        n_accidents=("n_accidents", "sum"), n_hours=("n_hours", "sum"),
        mean_solar=("mean_solar", "mean")).reset_index()
    monthly["rate"] = monthly["n_accidents"] / monthly["n_hours"] * 1000
    r, p = stats.pearsonr(monthly["mean_solar"], monthly["rate"])
    rows.append(("solar_rate_correlation", "station_months", "pearson_r", r))
    rows.append(("solar_rate_correlation", "station_months", "p_value", p))
    rows.append(("solar_rate_correlation", "station_months", "n", len(monthly)))
    return rows


def weather_ratios(cells):
    """Rain and frost rate ratios (vs. dry/no-frost cells) for a cell subset."""
    rain_ratio = rate_per_1000h(cells[cells["rain_share"] > 0.35]) / \
        rate_per_1000h(cells[cells["rain_share"] == 0])
    winter = cells[cells["month"].isin(WINTER_MONTHS)]
    frost_ratio = rate_per_1000h(winter[winter["frost_share"] > 0.35]) / \
        rate_per_1000h(winter[winter["frost_share"] == 0])
    return rain_ratio, frost_ratio


def analyze_rq3(cells, accidents):
    """Weather sensitivity index per federal state."""
    rows = []
    for state, state_cells in cells.groupby("state"):
        rain_ratio, frost_ratio = weather_ratios(state_cells)
        sensitivity = (rain_ratio + frost_ratio) / 2
        kind = "city_state" if state in CITY_STATES else "territorial_state"
        rows.append(("state_sensitivity", state, "rain_ratio", rain_ratio))
        rows.append(("state_sensitivity", state, "frost_ratio", frost_ratio))
        rows.append(("state_sensitivity", state, "sensitivity_index", sensitivity))
        rows.append(("state_sensitivity", state, "n_accidents",
                     state_cells["n_accidents"].sum()))
        rows.append(("state_kind", state, kind, 1))
    return rows


def analyze_rq4(cells, accidents):
    """Yearly evolution of the weather-related accident risk."""
    rows = []
    yearly_ratios = []
    for year, year_cells in cells.groupby("year"):
        rain_ratio, frost_ratio = weather_ratios(year_cells)
        year_accidents = accidents[accidents["year"] == year]
        bad_road = year_accidents[year_accidents["road_condition"] > 0]
        severe_share_bad = (bad_road["severity"] <= 2).mean()
        rows.append(("yearly_risk", str(year), "rain_ratio", rain_ratio))
        rows.append(("yearly_risk", str(year), "frost_ratio", frost_ratio))
        rows.append(("yearly_risk", str(year), "n_accidents", len(year_accidents)))
        rows.append(("yearly_risk", str(year), "share_severe_on_wet_or_icy",
                     severe_share_bad))
        yearly_ratios.append((year, rain_ratio))

    years = [y for y, _ in yearly_ratios]
    ratios = [r for _, r in yearly_ratios]
    trend = stats.linregress(years, ratios)
    rows.append(("rain_ratio_trend", "2016-2024", "slope_per_year", trend.slope))
    rows.append(("rain_ratio_trend", "2016-2024", "p_value", trend.pvalue))
    return rows


ANALYSES = {1: analyze_rq1, 2: analyze_rq2, 3: analyze_rq3, 4: analyze_rq4}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--rq", type=int, required=True, choices=ANALYSES,
                        help="research question to analyse")
    parser.add_argument("--table", default="data/processed/analysis_table.csv")
    parser.add_argument("--accidents", default="data/processed/accidents_stations.csv")
    parser.add_argument("--output", default=None,
                        help="output CSV (default: results/rq<N>_results.csv)")
    args = parser.parse_args(argv)
    output = args.output or f"results/rq{args.rq}_results.csv"

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    for path in (args.table, args.accidents):
        if not os.path.exists(path):
            log.error("input file %s not found", path)
            sys.exit(1)

    cells = pd.read_csv(args.table)
    accidents = pd.read_csv(args.accidents)
    log.info("analysing RQ%d on %d cells / %d accidents",
             args.rq, len(cells), len(accidents))

    rows = ANALYSES[args.rq](cells, accidents)
    result = pd.DataFrame(rows, columns=["section", "group", "metric", "value"])

    os.makedirs(os.path.dirname(output), exist_ok=True)
    result.to_csv(output, index=False)
    log.info("wrote %d result rows to %s", len(result), output)


if __name__ == "__main__":
    main()
