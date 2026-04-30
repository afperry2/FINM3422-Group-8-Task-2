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