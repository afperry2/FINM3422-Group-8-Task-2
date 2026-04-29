
# FINM3422 — A2 Teaching Dataset (Frozen Week 5, 2026)
## Multi‑Asset Performance, Risk & Attribution Assessment  
### READ THIS BEFORE USING THE DATA

This folder contains the **frozen dataset** for Assessment 2.  
All students must use the **same files** to ensure fairness, reproducibility, and consistent results.

---

## 1) What Each File Contains

### Benchmarks (monthly returns)
```
a2_release/benchmarks/
    aus_eq_bm.csv       # Australian Equities benchmark
    intl_eq_bm.csv      # International Equities benchmark
    bonds_bm.csv        # Bonds / Fixed Income benchmark
    re_bm.csv           # Real Estate benchmark
    pevc_bm.csv         # Private Equity / Venture Capital benchmark
```

Each file has:
```
Date,Return
YYYY-MM-30, 0.0123
...
```
- Returns are **monthly decimal returns** (e.g., 0.0123 = +1.23%).
- Benchmarks are aligned to the **same monthly index**.

### Manager Series (synthetic, teaching only)
```
a2_release/managers/
    aus_eq_mgr.csv
    intl_eq_mgr.csv
    bonds_mgr.csv
    re_mgr.csv
    pevc_mgr.csv
```

These represent the **manager returns** for each sleeve.

> **Note:** Manager returns are **synthetic** (artificially generated) and for **teaching use only**.  
> They are designed to look realistic and behave similarly to their benchmarks but do not represent any real fund.

### Risk‑Free Rate
```
rf_monthly.csv
```
Contains:
```
Date,RF
YYYY-MM-30, 0.0025
```
- `RF` is a **monthly decimal risk‑free rate**.
- Convert to annualised only if needed for a metric.

### Strategic Asset Allocation (SAA) Weights
```
saa_weights.csv
```
Contains:
```
Sleeve,Weight
AUS_EQ,0.40
INTL_EQ,0.30
BONDS,0.20
RE,0.05
PEVC,0.05
```
Used to compute the **composite benchmark** and perform **attribution**.

---

## 2) How to Load (Python)

Use `pandas`, with dates parsed and set as the index:

```python
import pandas as pd

bm = pd.read_csv(
    "data/a2_release/benchmarks/aus_eq_bm.csv",
    parse_dates=["Date"]
).set_index("Date")

bm.info()
bm.head()
```

---

## 3) Data Format

- **Monthly frequency** (month‑end): `YYYY‑MM‑30` (or the last day of each month).
- **Decimal returns (not %)**  
  - `0.012` → +1.2%  
  - `-0.034` → −3.4%
- **Returns, not prices** — do **not** convert to daily or other frequencies.

---

## 4) How to Align Indexes (Important)

All CSVs already have:
- Identical month‑end dates
- No missing months
- Same start and end date
- Sorted indices

When merging DataFrames:

```python
mgr = pd.read_csv("data/a2_release/managers/aus_eq_mgr.csv",
                  parse_dates=["Date"]).set_index("Date")

bm  = pd.read_csv("data/a2_release/benchmarks/aus_eq_bm.csv",
                  parse_dates=["Date"]).set_index("Date")

df = mgr.join(bm, how="inner", lsuffix="_mgr", rsuffix="_bm")
```

Sanity‑checks:

```python
df.index.is_monotonic_increasing
df.isna().sum()
df.index.freq  # may infer 'M'
```

---

## 5) Notes & Constraints

### 5.1 Synthetic Manager Series
Manager files (`*_mgr.csv`) contain **synthetic** returns created solely for FINM3422.

- They are *not* real funds.
- They are designed to behave realistically for metrics such as Sharpe, IR, alpha, and drawdown.
- Do **not** attempt to reverse‑engineer or analyse their construction.

### 5.2 Use Only the Provided Data
For Assessment 2:
- **Do not** replace or modify these CSVs.
- **Do not** use live APIs or other market data.
- **Do not** add external return series.

Your A2 analysis must be based **only** on the frozen dataset.

### 5.3 Decimal Returns Only
For example:
```python
wealth = (1 + df['Return']).cumprod()
```

---

## 6) Recommended Loading Pattern for A2

Example: AUS EQ manager + benchmark

```python
import pandas as pd

bm  = pd.read_csv("data/a2_release/benchmarks/aus_eq_bm.csv",
                  parse_dates=["Date"]).set_index("Date")
mgr = pd.read_csv("data/a2_release/managers/aus_eq_mgr.csv",
                  parse_dates=["Date"]).set_index("Date")

df = mgr.join(bm, how="inner", lsuffix="_mgr", rsuffix="_bm")
```

---

## 7) Quick Sanity Checks

After loading:
```python
df.isna().sum()          # should be zero
df.index.is_monotonic_increasing
df.describe()
```

After merging multiple sleeves:
```python
df.index.equals(other_df.index)  # True if aligned
```

Composite benchmark:
```python
weights = pd.read_csv("data/a2_release/saa_weights.csv")
# Compute weighted benchmark from sleeve benchmark returns
```

---

## 8) Final Reminder

This dataset is **frozen** for the semester to ensure **fairness** and **reproducibility**.  
If you have questions about the data, ask during tutorials.

Good luck with Assessment 2!

— **FINM3422 Teaching Team**
