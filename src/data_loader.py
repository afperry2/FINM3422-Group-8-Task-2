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