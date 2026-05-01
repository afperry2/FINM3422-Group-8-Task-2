# AMELIA

import pandas as pd
import numpy as np
import sys

def monthly_attribution(
    df_managers: pd.DataFrame, 
    df_benchmark: pd.DataFrame, 
    taa_weights: pd.Series, 
    saa_weights: pd.Series
    ) -> pd.DataFrame:
    
    # Compute monthly allocation and selection effects for each sleeve.

    # Parameters:
    # df_managers: pd.DataFrame - monthly manager returns (columns = sleeves)
    # df_benchmark: pd.DataFrame - monthly benchmark returns (columns = sleeves)
    # taa_weights: pd.Series - TAA weights by sleeve name
    # saa_weights: pd.Series - SAA weights by sleeve name
    
    # Returns:
    # df_allocation: pd.DataFrame - monthly allocation effects per sleeve
    # df_selection: pd.DataFrame - monthly selection effects per sleeve
    
    df_allocation = pd.DataFrame(index=df_managers.index, columns=df_managers.columns, dtype=float)
    df_selection = pd.DataFrame(index=df_managers.index, columns=df_managers.columns, dtype=float)

    for sleeve in df_managers.columns:
        w_taa = taa_weights[sleeve]
        w_saa = saa_weights[sleeve]
        r_bm = df_benchmark[sleeve]
        r_mgr = df_managers[sleeve]

        # Allocation effect: (w_taa - w_saa) * r_bm
        df_allocation[sleeve] = (w_taa - w_saa) * r_bm

        # Selection effect: w_taa * (r_mgr - r_bm)
        df_selection[sleeve] = w_saa * (r_mgr - r_bm)
    return df_allocation, df_selection

def brinson_attribution(
    df_managers: pd.DataFrame,
    df_benchmark: pd.DataFrame,
    taa_weights: pd.Series,
    saa_weights: pd.Series
    ) -> pd.DataFrame:
    
    # Aggregate monthly distribution to full-sample totals per sleeve
    # Returns:
    # pd.DataFrame: allocation effect, selection effect, total - rows = sleeves
    
    df_allocation, df_selection = monthly_attribution(df_managers, df_benchmark, taa_weights, saa_weights)
    results = {}
    for sleeve in df_managers.columns:
        alloc = df_allocation[sleeve].sum()
        select = df_selection[sleeve].sum()
        results[sleeve] = {
            "Allocation Effect": alloc,
            "Selection Effect": select,
            "Total Attribution": alloc + select}
    df_out = pd.DataFrame(results).T
    df_out.loc["Total"] = df_out.sum()
    return df_out

# GABBY

import pandas as pd
from src.performance import TAA_WEIGHTS, SAA_WEIGHTS

def compute_attribution(manager_data, benchmark_data):
    allocation_effect = {}
    selection_effect  = {}

    for asset in manager_data:
        allocation_effect[asset] = (
            (TAA_WEIGHTS[asset] - SAA_WEIGHTS[asset]) *
            benchmark_data[asset]
        )
        selection_effect[asset] = (
            SAA_WEIGHTS[asset] *
            (manager_data[asset] - benchmark_data[asset])
        )

    allocation_total = {asset: allocation_effect[asset].sum() for asset in manager_data}
    selection_total  = {asset: selection_effect[asset].sum()  for asset in manager_data}

    attribution_table = pd.DataFrame({
        "Allocation Effect": allocation_total,
        "Selection Effect":  selection_total
    })
    attribution_table["Total"] = (
        attribution_table["Allocation Effect"] +
        attribution_table["Selection Effect"]
    )
    return attribution_table.round(4)


# Mason

import pandas as pd
import numpy as np

def brinson_attribution(
    df_managers: pd.DataFrame,
    df_benchmarks: pd.DataFrame,
    taa_weights: dict,
    saa_weights: dict,
) -> dict:
    wp = pd.Series(taa_weights)
    wb = pd.Series(saa_weights)

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
        "Allocation Effect":   alloc_monthly.sum(axis=1).mean(),
        "Selection Effect":    selec_monthly.sum(axis=1).mean(),
        "Total Active Return": (fund_return - benchmark_return).mean(),
    })

    overview = pd.DataFrame({
        "SAA Weight":         wb,
        "TAA Weight":         wp,
        "Weight Diff":        wp - wb,
        "Allocation Effect":  alloc_monthly.mean(),
        "Selection Effect":   selec_monthly.mean(),
        "Total Contribution": summary["Total Active"],
    })

    return {
        "monthly":  {"allocation": alloc_monthly, "selection": selec_monthly},
        "summary":  summary,
        "totals":   totals,
        "overview": overview,   
    }