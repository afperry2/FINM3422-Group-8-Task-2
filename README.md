# Group 8 - FINM3422 Assessment 2
## Multi-Asset Portfolio Performance, Risk & Attribution
This repository contains Group 8's materials for Assessment Task 2 for the course code FINM3422

### Overview
This repository contains the code and report for Assessment Task 2 of FINM3422. The analysis evaluates the performance, risk characteristics, and attribution of a multi-asset superannuation fund across five asset-class sleeves: Australian Equities, International Equities, Fixed Income, Real Estate, and Private Equity/Venture Capital.

### Repository File Structure
.
├── AI_USAGE.md
├── README.md
├── data
│   ├── _README_A2_DATA.md
│   ├── benchmarks
│   │   ├── aus_eq_bm.csv
│   │   ├── bonds_bm.csv
│   │   ├── intl_eq_bm.csv
│   │   ├── pevc_bm.csv
│   │   └── re_bm.csv
│   ├── managers
│   │   ├── aus_eq_mgr.csv
│   │   ├── bonds_mgr.csv
│   │   ├── intl_eq_mgr.csv
│   │   ├── pevc_mgr.csv
│   │   └── re_mgr.csv
│   ├── rf_monthly.csv
│   └── saa_weight.csv
├── notebook
│   └── multi-asset_portfolio_performance_report.ipynb
└── src
    ├── __pycache__
    │   ├── attribution.cpython-313.pyc
    │   ├── data_loader.cpython-313.pyc
    │   ├── performance.cpython-313.pyc
    │   └── charts.cpython-313.pyc
    ├── attribution.py
    ├── data_loader.py
    ├── performance.py
    └── charts.py
7 directories, 24 files

### How to Run
1. Clone the repository and ensure all dependencies are installed (listed below)
2. Open the main notebook -> notebook/multi-asset_portfolio_performance_report.ipynb
3. Run all cells from top to bottom -> restart kernel and "run all"
** The notebook MUST be run from top to bottom. All functions are loaded from "/src" and running cells out of order will cause errors. **

### Dependencies
- python version 3.11 or newer
- pandas
- numpy
- matplotlib
- jupyter