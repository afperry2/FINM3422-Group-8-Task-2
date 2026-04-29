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