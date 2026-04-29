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


def load_managers(data_dir: str) -> pd.DataFrame:
    """
    Load all five sleeve manager return series.
    Returns a DataFrame: rows = months, columns = sleeve keys.
    """
    series = []
    for sleeve in SLEEVES:
        filename = f"managers/{sleeve}_mgr.csv"
        series.append(_load_single(data_dir, filename, sleeve))
    df = pd.concat(series, axis=1)
    df.sort_index(inplace=True)
    return df


def load_benchmarks(data_dir: str) -> pd.DataFrame:
    """
    Load all five sleeve benchmark return series.
    Returns a DataFrame: rows = months, columns = sleeve keys.
    """
    series = []
    for sleeve in SLEEVES:
        filename = f"benchmarks/{sleeve}_bm.csv"
        series.append(_load_single(data_dir, filename, sleeve))
    df = pd.concat(series, axis=1)
    df.sort_index(inplace=True)
    return df


def load_rf(data_dir: str) -> pd.Series:
    """Load the monthly risk-free rate proxy."""
    return _load_single(data_dir, "rf_monthly.csv", "rf")


def align_data(*dataframes) -> tuple:
    """
    Trim all DataFrames/Series to their common date range.
    Drops any rows with NaN values after alignment.
    """
    # Find common index
    common_index = dataframes[0].index
    for df in dataframes[1:]:
        common_index = common_index.intersection(df.index)

    aligned = []
    for df in dataframes:
        trimmed = df.loc[common_index].dropna()
        aligned.append(trimmed)

    # Use the shortest index after dropna
    final_index = aligned[0].index
    for df in aligned[1:]:
        final_index = final_index.intersection(df.index)

    return tuple(df.loc[final_index] for df in aligned)


def load_all_data(data_dir: str = "../data") -> dict:
    """
    Master loader — returns a dictionary with all cleaned data.

    Returns
    -------
    dict with keys:
        managers   : pd.DataFrame  — monthly manager returns (columns = sleeves)
        benchmarks : pd.DataFrame  — monthly benchmark returns (columns = sleeves)
        rf         : pd.Series     — monthly risk-free rate
        taa        : dict          — TAA weights
        saa        : dict          — SAA weights
    """
    managers   = load_managers(data_dir)
    benchmarks = load_benchmarks(data_dir)
    rf         = load_rf(data_dir)

    # Align all to common date range
    managers, benchmarks, rf = align_data(managers, benchmarks, rf)

    # Sanity checks
    assert not managers.isnull().any().any(),   "NaNs found in manager returns"
    assert not benchmarks.isnull().any().any(), "NaNs found in benchmark returns"
    assert not rf.isnull().any(),               "NaNs found in risk-free rate"
    assert list(managers.columns)   == SLEEVES, "Manager columns don't match sleeves"
    assert list(benchmarks.columns) == SLEEVES, "Benchmark columns don't match sleeves"

    print(f"Data loaded successfully.")
    print(f"   Date range : {managers.index[0].date()} → {managers.index[-1].date()}")
    print(f"   Months     : {len(managers)}")
    print(f"   Sleeves    : {SLEEVES}")

    return {
        "managers":   managers,
        "benchmarks": benchmarks,
        "rf":         rf,
        "taa":        TAA_WEIGHTS,
        "saa":        SAA_WEIGHTS,
    }