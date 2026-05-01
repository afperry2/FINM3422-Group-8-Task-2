# AMELIA

import pandas as pd
import numpy as np
import sys

# PERFORMANCE METRICS

# Parameters
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


# Full Portfolio (all sleeves)
def all_sleeves_summary(
    df_managers: pd.DataFrame,
    df_benchmarks: pd.DataFrame,
    df_rf: pd.Series
) -> pd.DataFrame:
    results = {}
    for sleeve in df_managers.columns:
        results[sleeve] = sleeve_summary(
            sleeve_name       = sleeve,
            monthly_returns   = df_managers[sleeve],
            monthly_bm = df_benchmarks[sleeve],
            monthly_rf        = df_rf.squeeze()   # convert single-col DataFrame to Series
        )
    return pd.DataFrame(results)

# GABBY

import numpy as np
import pandas as pd


def annualised_return(returns):
    returns = returns.dropna()
    n = len(returns)

    cumulative_return = (1 + returns).prod()
    ann_return = cumulative_return ** (12 / n) - 1

    return ann_return


def annualised_volatility(returns):
    returns = returns.dropna()
    return returns.std() * np.sqrt(12)


def sharpe_ratio(returns, risk_free_rate):
    ann_return = annualised_return(returns)
    ann_vol = annualised_volatility(returns)
    ann_rf = annualised_return(risk_free_rate)

    return (ann_return - ann_rf) / ann_vol


def tracking_error(portfolio_returns, benchmark_returns):
    active_returns = portfolio_returns - benchmark_returns
    return active_returns.std() * np.sqrt(12)


def information_ratio(portfolio_returns, benchmark_returns):
    active_returns = portfolio_returns - benchmark_returns

    ann_active_return = annualised_return(portfolio_returns) - annualised_return(benchmark_returns)
    te = tracking_error(portfolio_returns, benchmark_returns)

    return ann_active_return / te


def max_drawdown(returns):
    returns = returns.dropna()

    wealth_index = (1 + returns).cumprod()
    previous_peak = wealth_index.cummax()
    drawdown = (wealth_index - previous_peak) / previous_peak

    return drawdown.min()


def build_performance_table(manager_data, benchmark_data, rf):
    results = []
    for asset in manager_data:
        results.append({
            "Asset Class": asset,
            "Ann. Return": annualised_return(manager_data[asset]),
            "Ann. Volatility": annualised_volatility(manager_data[asset]),
            "Sharpe Ratio": sharpe_ratio(manager_data[asset], rf),
            "Tracking Error": tracking_error(manager_data[asset], benchmark_data[asset]),
            "Information Ratio": information_ratio(manager_data[asset], benchmark_data[asset]),
            "Max Drawdown": max_drawdown(manager_data[asset])
        })
    df = pd.DataFrame(results).set_index("Asset Class").round(4)
    return df


from src.performance import annualised_return, annualised_volatility, sharpe_ratio, max_drawdown

TAA_WEIGHTS = {
    "AUS EQ": 0.35, "INTL EQ": 0.35,
    "Bonds": 0.15, "Real Estate": 0.05, "PE/VC": 0.10
}

SAA_WEIGHTS = {
    "AUS EQ": 0.40, "INTL EQ": 0.30,
    "Bonds": 0.20, "Real Estate": 0.05, "PE/VC": 0.05
}

def compute_portfolio_returns(manager_data, benchmark_data):
    portfolio_return   = sum(manager_data[a]   * TAA_WEIGHTS[a] for a in TAA_WEIGHTS)
    benchmark_return   = sum(benchmark_data[a] * SAA_WEIGHTS[a] for a in SAA_WEIGHTS)
    return portfolio_return, benchmark_return

def build_fund_table(portfolio_return, benchmark_return, rf):
    data = {
        "Metric": ["Annualised Return", "Annualised Volatility", "Sharpe Ratio", "Max Drawdown"],
        "Total Fund": [
            annualised_return(portfolio_return),
            annualised_volatility(portfolio_return),
            sharpe_ratio(portfolio_return, rf),
            max_drawdown(portfolio_return)
        ],
        "Composite Benchmark": [
            annualised_return(benchmark_return),
            annualised_volatility(benchmark_return),
            sharpe_ratio(benchmark_return, rf),
            max_drawdown(benchmark_return)
        ]
    }
    return pd.DataFrame(data).set_index("Metric").round(4)


def run_apra_checks(portfolio_return, rf, cpi=0.02, target_spread=0.04,
                     vol_min=0.08, vol_max=0.12, drawdown_limit=-0.25,
                     equity_shock=-0.20):

    ann_ret = annualised_return(portfolio_return)
    ann_vol = annualised_volatility(portfolio_return)
    mdd     = max_drawdown(portfolio_return)
    target  = cpi + target_spread

    # Shock scenario — apply -20% equity shock to last month
    shocked_ret = (
        TAA_WEIGHTS["AUS EQ"]      * equity_shock +
        TAA_WEIGHTS["INTL EQ"]     * equity_shock +
        TAA_WEIGHTS["Bonds"]       * -0.02 +
        TAA_WEIGHTS["Real Estate"] * -0.02 +
        TAA_WEIGHTS["PE/VC"]       * -0.02
    )

    results = {
        "Check": [
            "1. Long-Run Return vs CPI + 4%",
            "2. Volatility Band (8–12%)",
            "3. Max Drawdown Threshold (> -25%)",
            "4. Equity Shock Scenario (-20%)"
        ],
        "Value": [
            f"{ann_ret:.2%}",
            f"{ann_vol:.2%}",
            f"{mdd:.2%}",
            f"{shocked_ret:.2%}"
        ],
        "Threshold": [
            f"≥ {target:.2%} (CPI {cpi:.0%} + {target_spread:.0%})",
            "8.00% – 12.00%",
            "> -25.00%",
            "Observe impact"
        ],
        "Pass": [
            "Pass" if ann_ret >= target else "Fail",
            "Below band" if ann_vol < vol_min else ("Pass" if ann_vol <= vol_max else "Fail"),
            "Pass" if mdd > drawdown_limit else "Fail",
            "Resilient" if shocked_ret > 0 else "Negative under shock"
        ]
    }
    return pd.DataFrame(results).set_index("Check")

# MASON

import pandas as pd
import numpy as np
import sys

# PERFORMANCE METRICS

# Parameters
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


# Full Portfolio (all sleeves)
def all_sleeves_summary(
    df_managers: pd.DataFrame,
    df_benchmarks: pd.DataFrame,
    df_rf: pd.Series
) -> pd.DataFrame:
    results = {}
    for sleeve in df_managers.columns:
        results[sleeve] = sleeve_summary(
            sleeve_name       = sleeve,
            monthly_returns   = df_managers[sleeve],
            monthly_bm = df_benchmarks[sleeve],
            monthly_rf        = df_rf.squeeze()   # convert single-col DataFrame to Series
        )
    return pd.DataFrame(results)

# APRA Checks (Simplified)

def apra_checks(
    df_managers: pd.DataFrame,
    df_rf: pd.Series,
    taa_weights: dict,
    cpi_assumption: float = 0.025,   # 2.5% assumed CPI
    return_target_spread: float = 0.03,  # CPI + 3%
    vol_limit: float = 0.12,         # 12% volatility cap
    drawdown_limit: float = -0.25,   # -25% drawdown threshold
) -> pd.DataFrame:
    """
    Simplified APRA-inspired checks on the total fund (TAA-weighted).

    Checks:
    1. Long-run return vs objective (CPI + X%)
    2. Volatility vs notional risk limit
    3. Maximum drawdown vs threshold
    """
    # Total fund return series with TAA weights
    weights = pd.Series(taa_weights)
    fund_returns = df_managers.mul(weights).sum(axis=1)

    # Compute metrics
    r_ann   = annualised_return(fund_returns)
    vol_ann = annualised_volatility(fund_returns)
    mdd     = max_drawdown(fund_returns)
    target  = cpi_assumption + return_target_spread

    # Results table
    checks = {
        "Long-Run Return vs Objective (CPI + 3%)": {
            "Actual":    f"{r_ann:.2%}",
            "Threshold": f"{target:.2%}",
            "Pass": "Pass" if r_ann >= target else "FAIL",
        },
        "Annualised Volatility vs Risk Limit (12%)": {
            "Actual":    f"{vol_ann:.2%}",
            "Threshold": f"{vol_limit:.2%}",
            "Pass": "Pass" if vol_ann <= vol_limit else "FAIL",
        },
        "Maximum Drawdown vs Threshold (-25%)": {
            "Actual":    f"{mdd:.2%}",
            "Threshold": f"{drawdown_limit:.2%}",
            "Pass": "Pass" if mdd >= drawdown_limit else "FAIL",
        },
    }

    return pd.DataFrame(checks).T
# Equity Markets Crash Scenario 1 - a 20$ reduction int he equity markets 

import pandas as pd

# Apply shock: 20% reduction in AUS_EQ and INTL_EQ for a single month we can choose the 3rd last month in the data (arbitrary choice for demonstration)

def equity_crash(df_managers: pd.DataFrame, taa_weights: dict) -> pd.DataFrame:
    taa = pd.Series(taa_weights)

    normal_returns = df_managers.iloc[-3].copy()
    return_normal  = (taa * normal_returns).sum()

    shock_a = normal_returns.copy()
    shock_a["aus_eq"]  = normal_returns["aus_eq"]  - 0.20
    shock_a["intl_eq"] = normal_returns["intl_eq"] - 0.20
    return_shock_a = (taa * shock_a).sum()

    return pd.DataFrame({
        "Scenario": ["Baseline", "A: Equity Crash (-20%)"],
        "Portfolio Return": [return_normal, return_shock_a],
        "Impact vs Baseline": [0, return_shock_a - return_normal],
    }).set_index("Scenario")

# SHock B is the bond yield spiking scenario 

import pandas as pd

def bond_yield_spike(
    df_managers: pd.DataFrame,
    taa_weights: dict,
    bond_duration: float = 4.0,   # adjust to your portfolio's duration
    rate_shock: float = 0.015,    # +150 bps = 1.5%
) -> pd.DataFrame:

    taa = pd.Series(taa_weights)

    normal_returns = df_managers.iloc[-3].copy()
    return_normal  = (taa * normal_returns).sum()

    # Bond shock = -(duration x rate_shock)
    bond_shock = -(bond_duration * rate_shock)   # e.g. -(5 x 0.015) = -7.5%

    shock_b = normal_returns.copy()
    shock_b["aus_eq"]  = normal_returns["aus_eq"]  - 0.02
    shock_b["intl_eq"] = normal_returns["intl_eq"] - 0.02
    shock_b["bonds"]   = normal_returns["bonds"]   + bond_shock
    shock_b["re"]      = normal_returns["re"]      - 0.05
    shock_b["pevc"]    = normal_returns["pevc"]    - 0.02

    return_shock_b = (taa * shock_b).sum()

    return pd.DataFrame({
        "Scenario": ["Baseline", "Bond Yield Spike (+150bps)"],
        "Portfolio Return":    [return_normal, return_shock_b],
        "Impact vs Baseline":  [0, return_shock_b - return_normal],
        "Bond Shock Applied":  [0, bond_shock],
    }).set_index("Scenario")