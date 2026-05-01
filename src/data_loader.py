import pandas as pd

# Load all manager, benchmark, risk-free and SAA weight data 
def load_data(base_path: str) -> tuple:
    BM_PATH   = base_path + "benchmarks/"
    MGR_PATH  = base_path + "managers/"
    SLEEVES = ["aus_eq", "intl_eq", "bonds", "re", "pevc"]
    
    df_rf  = pd.read_csv(base_path + "rf_monthly.csv", parse_dates=["Date"]).set_index("Date")
    df_saa = pd.read_csv(base_path + "saa_weight.csv", index_col="Sleeve")
    df_saa.index = df_saa.index.str.lower()
    
    df_benchmarks = pd.concat([
        pd.read_csv(BM_PATH + f"{s}_bm.csv", parse_dates=["Date"])
        .set_index("Date")
        .rename(columns={"Return": s})
        for s in SLEEVES
        ], axis=1)
    df_managers = pd.concat([
        pd.read_csv(MGR_PATH + f"{s}_mgr.csv", parse_dates=["Date"])
        .set_index("Date")
        .rename(columns={"Return": s})
        for s in SLEEVES
        ], axis=1)
    return df_managers, df_benchmarks, df_rf, df_saa



# Validate data before proceeding with analysis
# check for datetime index, matching dates, missing values, and sorted dates
def validate_data(df_managers, df_benchmarks, df_rf):
   assert isinstance(df_managers.index, pd.DatetimeIndex), "Managers index is not DatetimeIndex"
   assert isinstance(df_benchmarks.index, pd.DatetimeIndex), "Benchmarks index is not DatetimeIndex"
   assert isinstance(df_rf.index, pd.DatetimeIndex), "Risk-free index is not DatetimeIndex"
   
   assert df_managers.index.equals(df_benchmarks.index), "Managers and Benchmarks dates do not match"
   assert df_managers.index.equals(df_rf.index), "Managers and Risk-free dates do not match"
   
   assert df_managers.isna().sum().sum() == 0, "Managers data contains missing values"
   assert df_benchmarks.isna().sum().sum() == 0, "Benchmarks data contains missing values"
   assert df_rf.isna().sum().sum() == 0, "Risk-free data contains missing values"
   assert df_managers.index.is_monotonic_increasing, "Managers dates are not sorted"
   
   print("Data validation passed: All checks successful.")
   print(f"Date range: {df_managers.index[0].date()} to {df_managers.index[-1].date()}")
   print(f"Observations: {len(df_managers)} months")
   print(f"Sleeves: {list(df_managers.columns)}")

   # GABBY

import pandas as pd
import os

DATA_PATH = "../data"

def load_all_data():
    asset_classes = {
        "AUS EQ":      ("aus_eq_mgr.csv",  "aus_eq_bm.csv"),
        "INTL EQ":     ("intl_eq_mgr.csv", "intl_eq_bm.csv"),
        "Bonds":       ("bonds_mgr.csv",   "bonds_bm.csv"),
        "Real Estate": ("re_mgr.csv",      "re_bm.csv"),
        "PE/VC":       ("pevc_mgr.csv",    "pevc_bm.csv"),
    }

    manager_data, benchmark_data = {}, {}

    for asset, (mgr_file, bm_file) in asset_classes.items():
        mgr = pd.read_csv(f"{DATA_PATH}/managers/{mgr_file}",
                          parse_dates=["Date"], index_col="Date")
        bm  = pd.read_csv(f"{DATA_PATH}/benchmarks/{bm_file}",
                          parse_dates=["Date"], index_col="Date")

        # Sanity checks
        assert mgr.index.equals(bm.index), f"Date mismatch: {asset}"
        assert mgr["Return"].isna().sum() == 0, f"NAs in manager: {asset}"
        assert len(mgr) > 1, f"Insufficient data: {asset}"

        manager_data[asset]   = mgr["Return"]
        benchmark_data[asset] = bm["Return"]

    rf  = pd.read_csv(f"{DATA_PATH}/rf_monthly.csv",
                      parse_dates=["Date"], index_col="Date")["Return"]
    saa = pd.read_csv(f"{DATA_PATH}/saa_weight.csv")

    return manager_data, benchmark_data, rf, saa

# MASON

import pandas as pd
from pathlib import Path

# ── Sleeve identifiers ──────────────────────────────────────────────────────
SLEEVES = ["aus_eq", "intl_eq", "bonds", "re", "pevc"]

SLEEVE_LABELS = {
    "aus_eq":  "Australian Equities",
    "intl_eq": "International Equities",
    "bonds":   "Bonds",
    "re":      "Real Estate",
    "pevc":    "PE / VC",
}

# Constant TAA weights
TAA_WEIGHTS = {
    "aus_eq":  0.35,
    "intl_eq": 0.35,
    "bonds":   0.15,
    "re":      0.05,
    "pevc":    0.10,
}

# SAA weights
SAA_WEIGHTS = {
    "aus_eq":  0.40,
    "intl_eq": 0.30,
    "bonds":   0.20,
    "re":      0.05,
    "pevc":    0.05,
}


def _load_single(data_dir: str, filename: str, sleeve: str) -> pd.Series:
    """
    Load a single monthly return CSV file.
    Expects two columns: a date column and a return column.
    Returns a named pd.Series with a monthly DatetimeIndex (month-end).
    """
    filepath = Path(data_dir) / filename
    df = pd.read_csv(filepath, index_col=0, parse_dates=True)
    df.index = pd.to_datetime(df.index)
    df.index = df.index.to_period("M").to_timestamp("M")   # normalise to month-end
    series = df.squeeze()
    series.name = sleeve
    return series
