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
