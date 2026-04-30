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