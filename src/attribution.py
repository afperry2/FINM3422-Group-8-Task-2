import pandas as pd
import numpy as np

def brinson_attribution(
    df_managers: pd.DataFrame,
    df_benchmarks: pd.DataFrame,
    taa_weights: dict,
    saa_weights: dict,
) -> dict:
    wp = pd.Series(taa_weights)   # portfolio (TAA) weights
    wb = pd.Series(saa_weights)   # benchmark (SAA) weights

   
    fund_return      = df_managers.mul(wp).sum(axis=1)
    benchmark_return = df_benchmarks.mul(wb).sum(axis=1)

    alloc_monthly = pd.DataFrame(index=df_managers.index, columns=df_managers.columns, dtype=float)
    selec_monthly = pd.DataFrame(index=df_managers.index, columns=df_managers.columns, dtype=float)

    for sleeve in df_managers.columns:
        alloc_monthly[sleeve] = (wp[sleeve] - wb[sleeve]) * (df_benchmarks[sleeve] - benchmark_return)
        selec_monthly[sleeve] = wb[sleeve] * (df_managers[sleeve] - df_benchmarks[sleeve])

    summary = pd.DataFrame({
        "Allocation Effect": alloc_monthly.mean(),
        "Selection Effect":  selec_monthly.mean(),
    })
    summary["Total Active"] = summary["Allocation Effect"] + summary["Selection Effect"]

    totals = pd.Series({
        "Allocation Effect": alloc_monthly.sum(axis=1).mean(),
        "Selection Effect":  selec_monthly.sum(axis=1).mean(),
        "Total Active Return": (fund_return - benchmark_return).mean(),
    })

    return {
        "monthly": {"allocation": alloc_monthly, "selection": selec_monthly},
        "summary": summary,
        "totals":  totals,
    }