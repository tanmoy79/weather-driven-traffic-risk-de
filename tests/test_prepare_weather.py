"""Tests for prepare_weather.py."""

import zipfile

import pandas as pd
import pytest

import prepare_weather


def make_zip(path, content):
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("produkt_tu_stunde_test.txt", content)


def test_read_product_file_parses_values_and_missing(tmp_path):
    content = ("STATIONS_ID;MESS_DATUM;QN_9;TT_TU;RF_TU;eor\n"
               "44;2020010100;3;   5.2;  80;eor\n"
               "44;2020010101;3;-999;  81;eor\n")
    path = tmp_path / "stundenwerte_TU_00044_hist.zip"
    make_zip(path, content)

    df = prepare_weather.read_product_file(str(path), "TT_TU")
    assert df["TT_TU"].iloc[0] == pytest.approx(5.2)
    assert pd.isna(df["TT_TU"].iloc[1])  # -999 means missing
    assert df["timestamp"].iloc[0] == pd.Timestamp("2020-01-01 00:00")


def test_read_product_file_handles_solar_timestamps(tmp_path):
    # solar timestamps carry an extra ":MM" suffix
    content = ("STATIONS_ID;MESS_DATUM;QN_592;FG_LBERG;eor\n"
               "44;2020010112:00;1;  150;eor\n")
    path = tmp_path / "stundenwerte_ST_00044_row.zip"
    make_zip(path, content)

    df = prepare_weather.read_product_file(str(path), "FG_LBERG")
    assert df["timestamp"].iloc[0] == pd.Timestamp("2020-01-01 12:00")


def test_read_product_file_rejects_missing_column(tmp_path):
    content = "STATIONS_ID;MESS_DATUM;QN_9;OTHER;eor\n44;2020010100;3;1;eor\n"
    path = tmp_path / "stundenwerte_TU_00044_hist.zip"
    make_zip(path, content)
    with pytest.raises(ValueError, match="TT_TU"):
        prepare_weather.read_product_file(str(path), "TT_TU")


def test_to_local_complete_series_fills_gaps():
    df = pd.DataFrame({
        "timestamp": pd.to_datetime(["2020-06-01 10:00", "2020-06-01 13:00"]),
        "temp_c": [15.0, 18.0],
    })
    result = prepare_weather.to_local_complete_series(df, 2020, 2020)

    # a leap year has 366 * 24 hours
    assert len(result) == 366 * 24
    # 10:00 UTC is 12:00 local time in June (CEST)
    assert result.loc["2020-06-01 12:00+02:00", "temp_c"] == 15.0
    assert pd.isna(result.loc["2020-06-01 13:00+02:00", "temp_c"])
