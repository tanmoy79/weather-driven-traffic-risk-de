"""Download hourly DWD weather data from the Climate Data Center.

Downloads hourly air temperature, precipitation and solar radiation
observations from https://opendata.dwd.de/ (license: CC-BY 4.0, see
data/raw_weather/README after download). Only stations that measure all
three parameters over the whole analysis period are used, and per federal
state at most --stations-per-state stations are selected so that the
download stays manageable.

Usage:
    python src/download_weather.py --start-year 2016 --end-year 2024 \
        --stations-per-state 2 --out-dir data/raw_weather
"""

import argparse
import logging
import os
import re
import sys

import pandas as pd
import requests

log = logging.getLogger("download_weather")

BASE_URL = "https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly"

# parameter -> (subdirectory, station description file, zip name prefix)
PARAMETERS = {
    "air_temperature": ("air_temperature/historical", "TU_Stundenwerte_Beschreibung_Stationen.txt", "stundenwerte_TU_"),
    "precipitation": ("precipitation/historical", "RR_Stundenwerte_Beschreibung_Stationen.txt", "stundenwerte_RR_"),
    "solar": ("solar", "ST_Stundenwerte_Beschreibung_Stationen.txt", "stundenwerte_ST_"),
}


def fetch(url, timeout=60):
    """Download a URL and return the response, exiting with a message on failure."""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as err:
        log.error("download failed for %s: %s", url, err)
        sys.exit(1)
    return response


def parse_station_list(text):
    """Parse a DWD station description file into a dataframe."""
    rows = []
    for line in text.splitlines()[2:]:  # first two lines are header + dashes
        parts = line.split()
        if len(parts) < 8:
            continue
        # layout: id, from, to, height, lat, lon, name..., state [, "Frei"]
        state = parts[-1] if parts[-1] != "Frei" else parts[-2]
        name_end = -1 if parts[-1] != "Frei" else -2
        rows.append({
            "station_id": int(parts[0]),
            "from_date": parts[1],
            "to_date": parts[2],
            "lat": float(parts[4]),
            "lon": float(parts[5]),
            "name": " ".join(parts[6:name_end]),
            "state": state,
        })
    return pd.DataFrame(rows)


def select_stations(station_lists, start_year, end_year, per_state):
    """Pick a few stations per state that cover the whole period.

    Temperature and precipitation are required (the station network for
    these is dense), solar radiation is only measured at a few dozen
    stations and is therefore optional. Stations with solar are preferred
    so that as many of them as possible end up in the selection.
    """
    start, end = f"{start_year}0101", f"{end_year}1231"
    covered = {}
    for param, stations in station_lists.items():
        ok = stations[(stations["from_date"] <= start) & (stations["to_date"] >= end)]
        covered[param] = set(ok["station_id"])
        log.info("%s: %d stations cover %s-%s", param, len(ok), start_year, end_year)
    required = covered["air_temperature"] & covered["precipitation"]

    meta = station_lists["air_temperature"]
    meta = meta[meta["station_id"].isin(required)].copy()
    meta["has_solar"] = meta["station_id"].isin(covered["solar"])
    meta = meta.sort_values(["has_solar", "station_id"], ascending=[False, True])
    selected = meta.groupby("state").head(per_state).sort_values("station_id")
    return selected[["station_id", "name", "state", "lat", "lon", "has_solar"]]


def download_station_files(stations, out_dir, timeout):
    """Download the zip archive of every selected station for each parameter."""
    for param, (subdir, _, prefix) in PARAMETERS.items():
        index_html = fetch(f"{BASE_URL}/{subdir}/", timeout).text
        zip_names = re.findall(rf'{prefix}\d{{5}}[^"]*?\.zip', index_html)
        param_dir = os.path.join(out_dir, param)
        os.makedirs(param_dir, exist_ok=True)

        for _, station in stations.iterrows():
            station_id = station["station_id"]
            if param == "solar" and not station["has_solar"]:
                continue
            wanted = [z for z in zip_names if z.startswith(f"{prefix}{station_id:05d}_")]
            if not wanted:
                log.warning("no %s file found for station %d, skipping", param, station_id)
                continue
            target = os.path.join(param_dir, wanted[0])
            if os.path.exists(target):
                log.info("already downloaded: %s", wanted[0])
                continue
            data = fetch(f"{BASE_URL}/{subdir}/{wanted[0]}", timeout).content
            with open(target, "wb") as fh:
                fh.write(data)
            log.info("downloaded %s (%.1f MB)", wanted[0], len(data) / 1e6)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--start-year", type=int, default=2016)
    parser.add_argument("--end-year", type=int, default=2024)
    parser.add_argument("--stations-per-state", type=int, default=2,
                        help="maximum number of stations per federal state")
    parser.add_argument("--out-dir", default="data/raw_weather")
    parser.add_argument("--timeout", type=int, default=60,
                        help="download timeout in seconds")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    station_lists = {}
    for param, (subdir, description_file, _) in PARAMETERS.items():
        response = fetch(f"{BASE_URL}/{subdir}/{description_file}", args.timeout)
        station_lists[param] = parse_station_list(response.content.decode("latin-1"))

    stations = select_stations(station_lists, args.start_year, args.end_year,
                               args.stations_per_state)
    if stations.empty:
        log.error("no stations cover the requested period %d-%d",
                  args.start_year, args.end_year)
        sys.exit(1)
    log.info("selected %d stations in %d states",
             len(stations), stations["state"].nunique())

    os.makedirs(args.out_dir, exist_ok=True)
    stations_file = os.path.join(args.out_dir, "stations.csv")
    stations.to_csv(stations_file, index=False)
    log.info("wrote station list to %s", stations_file)

    download_station_files(stations, args.out_dir, args.timeout)
    log.info("weather download finished")


if __name__ == "__main__":
    main()
