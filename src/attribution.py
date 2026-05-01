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
