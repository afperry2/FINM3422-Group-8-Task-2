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
    │   └── visuals.cpython-313.pyc
    ├── attribution.py
    ├── data_loader.py
    ├── performance.py
    └── visuals.py
7 directories, 24 files

### How to Run
add steps to run code...
The "multi-asset_portfolio_performance_report.ipynb" notebook should be used to access all tables, graphs and relevant results alongside detailed analysis for the tasks outlined in Assessment Task 2. The notebook should be run from top to bottom, to exercise relevant loading and produce necessary output, with the bodies of code separated into the files contained in the "src" folder (data_loading, performance, visuals, attribution).

### Dependencies
- python version 3.? or later
- pandas
- numpy
- matplotlib
- jupyter