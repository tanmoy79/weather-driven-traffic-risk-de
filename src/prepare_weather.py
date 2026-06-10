"""Turn the downloaded DWD zip archives into one clean hourly weather table.

For every selected station the script reads the product files for air
temperature (TT_TU), precipitation (R1) and global solar radiation (FG_LBERG),
replaces the DWD missing-value marker (-999) with NaN, converts the UTC
timestamps to local time (Europe/Berlin) and reindexes everything to a
complete, gap-free hourly time series for the analysis period.

Usage:
    python src/prepare_weather.py --raw-dir data/raw_weather \
        --start-year 2016 --end-year 2024 --output data/processed/weather_hourly.csv
"""

import argparse
import glob
import logging
import os
import sys
import zipfile

import pandas as pd

log = logging.getLogger("prepare_weather")

# parameter -> (zip name prefix, column in the product file, column in our output)
PARAMETERS = {
    "air_temperature": ("stundenwerte_TU_", "TT_TU", "temp_c"),
    "precipitation": ("stundenwerte_RR_", "R1", "precip_mm"),
    "solar": ("stundenwerte_ST_", "FG_LBERG", "solar_j_cm2"),
}

MISSING_VALUE = -999


def read_product_file(zip_path, value_column):
    """Read the data file inside a DWD zip archive and return time + value."""
    with zipfile.ZipFile(zip_path) as archive:
        product_names = [n for n in archive.namelist() if n.startswith("produkt")]
        if not product_names:
            raise ValueError(f"no product file inside {zip_path}")
        with archive.open(product_names[0]) as fh:
            df = pd.read_csv(fh, sep=";", skipinitialspace=True)

    df.columns = df.columns.str.strip()
    if value_column not in df.columns:
        raise ValueError(f"column {value_column} not found in {zip_path}")

    # solar timestamps look like "2016010100:00", the others like "2016010100"
    timestamp = pd.to_datetime(df["MESS_DATUM"].astype(str).str[:10],
                               format="%Y%m%d%H")
    values = pd.to_numeric(df[value_column], errors="coerce")
    values = values.where(values != MISSING_VALUE)
    return pd.DataFrame({"timestamp": timestamp, value_column: values})


def load_station(station_id, raw_dir):
    """Combine the parameters of one station into a single dataframe.

    Temperature and precipitation are required, solar radiation is optional
    (only a few stations measure it; the column stays NaN for the others).
    """
    combined = None
    for param, (prefix, value_column, out_name) in PARAMETERS.items():
        pattern = os.path.join(raw_dir, param, f"{prefix}{station_id:05d}_*.zip")
        matches = glob.glob(pattern)
        if not matches:
            if param == "solar":
                combined[out_name] = float("nan")
                continue
            log.warning("station %d: no %s archive found, skipping station",
                        station_id, param)
            return None
        df = read_product_file(matches[0], value_column)
        df = df.rename(columns={value_column: out_name})
        df = df.drop_duplicates(subset="timestamp")
        combined = df if combined is None else combined.merge(
            df, on="timestamp", how="outer")
    return combined


def to_local_complete_series(df, start_year, end_year):
    """Convert UTC to local time and reindex to a gap-free hourly series."""
    df = df.set_index("timestamp").sort_index()
    df.index = df.index.tz_localize("UTC").tz_convert("Europe/Berlin")
    full_index = pd.date_range(start=f"{start_year}-01-01 00:00",
                               end=f"{end_year}-12-31 23:00",
                               freq="h", tz="Europe/Berlin")
    return df.reindex(full_index)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--raw-dir", default="data/raw_weather",
                        help="directory with the downloaded DWD archives")
    parser.add_argument("--start-year", type=int, default=2016)
    parser.add_argument("--end-year", type=int, default=2024)
    parser.add_argument("--output", default="data/processed/weather_hourly.csv")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    stations_file = os.path.join(args.raw_dir, "stations.csv")
    if not os.path.exists(stations_file):
        log.error("%s not found, run download_weather.py first", stations_file)
        sys.exit(1)
    stations = pd.read_csv(stations_file)

    frames = []
    for station_id in stations["station_id"]:
        try:
            df = load_station(station_id, args.raw_dir)
        except (ValueError, OSError, zipfile.BadZipFile) as err:
            log.error("station %d: %s", station_id, err)
            sys.exit(1)
        if df is None:
            continue
        df = to_local_complete_series(df, args.start_year, args.end_year)
        df["station_id"] = station_id
        missing = df["temp_c"].isna().mean() * 100
        log.info("station %5d: %d hours prepared (%.1f%% temperature missing)",
                 station_id, len(df), missing)
        frames.append(df.reset_index(names="timestamp"))

    if not frames:
        log.error("no station data could be prepared")
        sys.exit(1)

    weather = pd.concat(frames, ignore_index=True)
    weather = weather[["station_id", "timestamp", "temp_c", "precip_mm", "solar_j_cm2"]]

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    weather.to_csv(args.output, index=False)
    log.info("wrote %d hourly rows for %d stations to %s",
             len(weather), weather["station_id"].nunique(), args.output)


if __name__ == "__main__":
    main()
