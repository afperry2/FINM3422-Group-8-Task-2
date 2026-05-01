import pandas as pd
import numpy as np

# PERFORMANCE METRICS

# monthly_returns: pd.Series - monthly decimal returns of mananager
# monthly_bm: pd.Series - monthly decimal returns of benchmark
# monthly_rf: pd.Series - monthly decimal risk-free rate return


# Annualised Return
def annualised_return(monthly_returns: pd.Series) -> float:
    n = len(monthly_returns)
    compounded = (1 + monthly_returns).prod()
    return compounded ** (12 / n) - 1

# Annualised Volatility
def annualised_volatility(monthly_returns: pd.Series) -> float:
    return monthly_returns.std() * np.sqrt(12)

# Sharpe Ratio
def sharpe_ratio(monthly_returns: pd.Series, monthly_rf: pd.Series) -> float:
    monthly_returns, monthly_rf = monthly_returns.align(monthly_rf, join="inner")
    r_ann = annualised_return(monthly_returns)
    rf_ann = annualised_return(monthly_rf)
    sigma = annualised_volatility(monthly_returns)
    if sigma == 0:
        return np.nan
    return (r_ann - rf_ann) / sigma

# Information Ratio
def information_ratio(monthly_returns: pd.Series, monthly_bm: pd.Series) -> float:
    r_ann = annualised_return(monthly_returns)
    rb_ann = annualised_return(monthly_bm)
    te = tracking_error(monthly_returns, monthly_bm)
    if te == 0:
        return np.nan
    return (r_ann - rb_ann) / te

# RISK METRICS

# Tracking Error vs Benchmark
def tracking_error(monthly_returns: pd.Series, monthly_bm: pd.Series) -> float:
    active = monthly_returns - monthly_bm
    return active.std() * np.sqrt(12)


# Maximum Drawdown
def max_drawdown(monthly_returns: pd.Series) -> float:
    wealth = (1 + monthly_returns).cumprod()
    rolling_max = wealth.cummax()
    drawdowns = (wealth - rolling_max) / rolling_max
    return drawdowns.min()

# SUMMARY PERFORMANCE AND RISK

# Parameters:
# sleeve_name: str - name of the sleeve (e.g., "aus_eq")
# monthly_returns: pd.Series - manager monthly returns
# monthly_bm: pd.Series - benchmark monthly returns
# monthtly_rf: pd.Series - risk-free monthly returns
# df_managers: pd.DataFrame - all manager returns (columns=sleeves)
# df_benchmarks: pd.DataFrame - all benchmark returns (columns=sleeves)
# df_rf: pd.DataFrame - monthly risk-free returns (single column)

# Summary (all metrics for a given sleeve)
def sleeve_summary(sleeve_name: str, monthly_returns: pd.Series, monthly_bm: pd.Series, monthly_rf: pd.Series) -> pd.Series:
    return pd.Series ({
        "Annualised Return (Manager)": annualised_return(monthly_returns),
        "Annualised Return (Benchmark)": annualised_return(monthly_bm),
        "Annualised Volatility": annualised_volatility(monthly_returns),
        "Sharpe Ratio": sharpe_ratio(monthly_returns, monthly_rf),
        "Tracking Error": tracking_error(monthly_returns, monthly_bm),
        "Information Ratio": information_ratio(monthly_returns, monthly_bm),
        "Maximum Drawdown (Manager)": max_drawdown(monthly_returns),
        "Maximum Drawdown (Benchmark)": max_drawdown(monthly_bm)
    }, name=sleeve_name)

def all_sleeves_summary(
    df_managers: pd.DataFrame,
    df_benchmarks: pd.DataFrame,
    df_rf: pd.Series
) -> pd.DataFrame:
    """Run sleeve_summary() across all sleeves and return a combined DataFrame."""
    results = {}
    for sleeve in df_managers.columns:
        results[sleeve] = sleeve_summary(
            sleeve_name     = sleeve,
            monthly_returns = df_managers[sleeve],
            monthly_bm      = df_benchmarks[sleeve],
            monthly_rf      = df_rf.squeeze()
        )
    return pd.DataFrame(results)

def display_summary_tables(summary: pd.DataFrame) -> None:
    """
    Display formatted performance and risk summary tables.
    summary : output of all_sleeves_summary()
    """
    pct_rows = [
        "Annualised Return (Manager)",
        "Annualised Return (Benchmark)",
        "Annualised Volatility",
        "Tracking Error",
        "Maximum Drawdown (Manager)",
        "Maximum Drawdown (Benchmark)",
    ]
    ratio_rows = ["Sharpe Ratio", "Information Ratio"]

    print("Table 1: Performance & Risk Summary (%)")
    print("Table 2: Ratios")

# --- APRA-INSPIRED CHECKS ---
 
def apra_checks(
    df_fund_monthly: pd.Series,
    cpi_assumption: float = 0.025,
    return_target_spread: float = 0.035,
    vol_limit: float = 0.10,
    drawdown_limit: float = -0.25,
) -> pd.DataFrame:
    """
    Simplified APRA-inspired checks on the total fund monthly return series.
 
    Parameters
    ----------
    df_fund_monthly      : pd.Series — TAA-weighted total fund monthly returns
    cpi_assumption       : float     — assumed CPI (default 2.5%)
    return_target_spread : float     — required spread above CPI (default 3.5%)
    vol_limit            : float     — maximum acceptable volatility (default 10%)
    drawdown_limit       : float     — maximum acceptable drawdown (default -25%)
    """
    r_ann   = annualised_return(df_fund_monthly)
    vol_ann = annualised_volatility(df_fund_monthly)
    mdd     = max_drawdown(df_fund_monthly)
    target  = cpi_assumption + return_target_spread
 
    checks = {
        "Long-Run Return vs Objective (CPI + 3.5%)": {
            "Fund Value":  f"{r_ann:.2%}",
            "Threshold":   f"{target:.2%}",
            "Pass / Fail": "Pass" if r_ann >= target else "Fail",
        },
        "Annualised Volatility vs Risk Limit (10%)": {
            "Fund Value":  f"{vol_ann:.2%}",
            "Threshold":   f"{vol_limit:.2%}",
            "Pass / Fail": "Pass" if vol_ann <= vol_limit else "Fail",
        },
        "Maximum Drawdown vs Threshold (-25%)": {
            "Fund Value":  f"{mdd:.2%}",
            "Threshold":   f"{drawdown_limit:.2%}",
            "Pass / Fail": "Pass" if mdd >= drawdown_limit else "Fail",
        },
    }
    return pd.DataFrame(checks).T
 
 
# --- SHOCK SCENARIOS ---
 
def equity_crash(
    df_managers: pd.DataFrame,
    taa_weights: dict,
    shock: float = 0.20,
) -> pd.DataFrame:
    """
    Shock Scenario A — simultaneous equity crash.
    Applies a -shock return to AUS EQ and INTL EQ for a single reference month.
    All other sleeves retain normal returns.
    """
    taa = pd.Series(taa_weights)
    normal_returns = df_managers.iloc[-3].copy()
    return_normal  = (taa * normal_returns).sum()
 
    shocked = normal_returns.copy()
    shocked["aus_eq"]  = normal_returns["aus_eq"]  - shock
    shocked["intl_eq"] = normal_returns["intl_eq"] - shock
    return_shocked = (taa * shocked).sum()
 
    return pd.DataFrame({
        "Scenario":         ["Normal (baseline)", f"Equity Crash (-{shock:.0%})"],
        "AUS EQ Return":    [f"{normal_returns['aus_eq']:.2%}",  f"{shocked['aus_eq']:.2%}"],
        "INTL EQ Return":   [f"{normal_returns['intl_eq']:.2%}", f"{shocked['intl_eq']:.2%}"],
        "Portfolio Return": [f"{return_normal:.2%}", f"{return_shocked:.2%}"],
        "Impact vs Normal": ["-", f"{return_shocked - return_normal:.2%}"],
    })
 
 
def bond_yield_spike(
    df_managers: pd.DataFrame,
    taa_weights: dict,
    bond_duration: float = 4.0,
    rate_shock: float = 0.015,
) -> pd.DataFrame:
    """
    Shock Scenario B — bond yield spike (+150bps).
    Bond shock = -(duration x rate_shock).
    Spillover effects applied across all asset classes.
    """
    taa = pd.Series(taa_weights)
    normal_returns = df_managers.iloc[-3].copy()
    return_normal  = (taa * normal_returns).sum()
 
    # Bond price change approximation: -(duration x rate shock)
    bond_shock = -(bond_duration * rate_shock)
 
    shocked = normal_returns.copy()
    shocked["aus_eq"]  = normal_returns["aus_eq"]  - 0.02
    shocked["intl_eq"] = normal_returns["intl_eq"] - 0.02
    shocked["bonds"]   = normal_returns["bonds"]   + bond_shock
    shocked["re"]      = normal_returns["re"]      - 0.05
    shocked["pevc"]    = normal_returns["pevc"]    - 0.02
    return_shocked = (taa * shocked).sum()
 
    return pd.DataFrame({
        "Scenario":         ["Normal (baseline)", "Bond Yield Spike (+150bps)"],
        "AUS EQ":           [f"{normal_returns['aus_eq']:.2%}",  f"{shocked['aus_eq']:.2%}"],
        "INTL EQ":          [f"{normal_returns['intl_eq']:.2%}", f"{shocked['intl_eq']:.2%}"],
        "Bonds":            [f"{normal_returns['bonds']:.2%}",   f"{shocked['bonds']:.2%}"],
        "RE":               [f"{normal_returns['re']:.2%}",      f"{shocked['re']:.2%}"],
        "PE/VC":            [f"{normal_returns['pevc']:.2%}",    f"{shocked['pevc']:.2%}"],
        "Portfolio Return": [f"{return_normal:.2%}", f"{return_shocked:.2%}"],
        "Impact vs Normal": ["-", f"{return_shocked - return_normal:.2%}"],
    })

# Total Fund Vs. Benchmark Comparison

def fund_vs_benchmark(
    df_fund_monthly: pd.Series,
    df_benchmark_monthly: pd.Series
) -> pd.DataFrame:
    """Comparison table of total fund vs composite benchmark metrics."""
    return pd.DataFrame({
        "Metric": ["Annualised Return", "Annualised Volatility", "Maximum Drawdown"],
        "Total Fund (TAA)": [
            f"{annualised_return(df_fund_monthly):.2%}",
            f"{annualised_volatility(df_fund_monthly):.2%}",
            f"{max_drawdown(df_fund_monthly):.2%}"
        ],
        "Composite Benchmark (SAA)": [
            f"{annualised_return(df_benchmark_monthly):.2%}",
            f"{annualised_volatility(df_benchmark_monthly):.2%}",
            f"{max_drawdown(df_benchmark_monthly):.2%}"
        ]
    })