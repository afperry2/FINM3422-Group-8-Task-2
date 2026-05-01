import pandas as pd
from pathlib import Path

SLEEVES = ["aus_eq", "intl_eq", "bonds", "re", "pevc"]

SLEEVE_LABELS = {
    "aus_eq":  "Australian Equities",
    "intl_eq": "International Equities",
    "bonds":   "Bonds",
    "re":      "Real Estate",
    "pevc":    "PE / VC",
}

# TAA weights
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


def load_single(data_dir: str, filename: str, sleeve: str) -> pd.Series:
    """
    Load a single monthly return CSV file.
    Returns a named pd.Series with a normalised month-end DatetimeIndex.
    """
    filepath = Path(data_dir) / filename
    df = pd.read_csv(filepath, index_col=0, parse_dates=True)
    df.index = pd.to_datetime(df.index)
    df.index = df.index.to_period("M").to_timestamp("M")  # normalise to month-end
    series = df.squeeze()
    series.name = sleeve
    return series


def load_managers(data_dir: str) -> pd.DataFrame:
    series = []
    for sleeve in SLEEVES:
        series.append(load_single(data_dir, f"managers/{sleeve}_mgr.csv", sleeve))
    df = pd.concat(series, axis=1)
    df.sort_index(inplace=True)
    return df


def load_benchmarks(data_dir: str) -> pd.DataFrame:
    series = []
    for sleeve in SLEEVES:
        series.append(load_single(data_dir, f"benchmarks/{sleeve}_bm.csv", sleeve))
    df = pd.concat(series, axis=1)
    df.sort_index(inplace=True)
    return df


def load_rf(data_dir: str) -> pd.Series:
    return load_single(data_dir, "rf_monthly.csv", "rf")


def align_data(*dataframes) -> tuple:
    common_index = dataframes[0].index
    for df in dataframes[1:]:
        common_index = common_index.intersection(df.index)

    aligned = [df.loc[common_index].dropna() for df in dataframes]

    final_index = aligned[0].index
    for df in aligned[1:]:
        final_index = final_index.intersection(df.index)

    return tuple(df.loc[final_index] for df in aligned)


# Load all Data and Validate
def load_all_data(data_dir: str = "../data") -> dict:
    managers   = load_managers(data_dir)
    benchmarks = load_benchmarks(data_dir)
    rf         = load_rf(data_dir)

    # Align Data Range
    managers, benchmarks, rf = align_data(managers, benchmarks, rf)

    # Validation checks
    assert not managers.isnull().any().any(),        "NaNs found in manager returns"
    assert not benchmarks.isnull().any().any(),      "NaNs found in benchmark returns"
    assert not rf.isnull().any(),                    "NaNs found in risk-free rate"
    assert managers.index.equals(benchmarks.index),  "Manager/benchmark date mismatch"
    assert list(managers.columns)   == SLEEVES,      "Manager columns do not match sleeves"
    assert list(benchmarks.columns) == SLEEVES,      "Benchmark columns do not match sleeves"
    assert managers.index.is_monotonic_increasing,   "Index is not sorted"

    print("Data loaded and validated successfully.")
    print(f"   Date range : {managers.index[0].date()} to {managers.index[-1].date()}")
    print(f"   Months     : {len(managers)}")
    print(f"   Sleeves    : {SLEEVES}")

    return {
        "managers":   managers,
        "benchmarks": benchmarks,
        "rf":         rf,
        "taa":        TAA_WEIGHTS,
        "saa":        SAA_WEIGHTS,
    }