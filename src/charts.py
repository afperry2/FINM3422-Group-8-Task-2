import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Section 3.2 - Sleeve Level Charts

def plot_sleeve_wealth_index(manager_data, benchmark_data, sleeve_labels):
    assets = list(manager_data.keys())
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    axes = axes.flatten()
    fig_labels = ["Figure 1a", "Figure 1b", "Figure 1c", "Figure 1d", "Figure 1e"]

    for i, asset in enumerate(assets):
        mgr_wealth = (1 + manager_data[asset]).cumprod()
        bm_wealth  = (1 + benchmark_data[asset]).cumprod()

        axes[i].plot(mgr_wealth.index, mgr_wealth.values, label="Manager", color="#FF6F3C")
        axes[i].plot(bm_wealth.index, bm_wealth.values,  label="Benchmark", color="#0B6623", linestyle="--")
        axes[i].set_title(f"{fig_labels[i]}: {sleeve_labels.get(asset, asset)}")
        axes[i].set_xlabel("Month")
        axes[i].set_ylabel("Wealth Index")
        axes[i].tick_params(axis='x', rotation=45)
        axes[i].legend(fontsize=8)

    axes[-1].set_visible(False)
    fig.suptitle("Figure 1: Sleeve-Level Cumulative Returns — Manager vs Benchmark",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.show()

def plot_sleeve_vs_benchmark(
    fund_returns,
    benchmark_returns,
    title: str = "Total Fund vs Composite Benchmark — Cumulative Wealth",
    figsize: tuple = (14, 6),
    save_path: str = None,
):
    wealth_fund = (1 + fund_returns).cumprod()
    wealth_bm   = (1 + benchmark_returns).cumprod()

    fig, ax = plt.subplots(figsize=figsize)

    # ── Shading: green where fund > benchmark, orange where fund < benchmark
    ax.fill_between(
        wealth_fund.index,
        wealth_fund,
        wealth_bm,
        where=(wealth_fund >= wealth_bm),
        interpolate=True,
        alpha=0.25,
        color="green",
        label="Outperformance",
    )
    ax.fill_between(
        wealth_fund.index,
        wealth_fund,
        wealth_bm,
        where=(wealth_fund < wealth_bm),
        interpolate=True,
        alpha=0.25,
        color="orange",
        label="Underperformance",
    )    
    # ── Lines ──────────────────────────────────────────────────────────────
    ax.plot(wealth_fund, color="#1a5fb4", linewidth=1.8, label="Total Fund (TAA)")
    ax.plot(wealth_bm,   color="#a52a2a", linewidth=1.4, linestyle="--", label="Composite Benchmark (SAA)")

    # ── Labels & formatting ────────────────────────────────────────────────
    ax.set_title(title, fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Date", fontsize=11)
    ax.set_ylabel("Wealth Index (start = 1.0)", fontsize=11)
    ax.legend(loc="upper left", framealpha=0.9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(wealth_fund.index[0], wealth_fund.index[-1])

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Chart saved to {save_path}")

    plt.show()

def plot_fund_vs_benchmark(portfolio_return, benchmark_return):
    wealth_fund = (1 + portfolio_return).cumprod()
    wealth_bm   = (1 + benchmark_return).cumprod()
    fig, ax = plt.subplots(figsize=(14, 6))

    ax.fill_between(
        wealth_fund.index, wealth_fund, wealth_bm,
        where=(wealth_fund >= wealth_bm),
        interpolate=True, alpha=0.25, color="yellow", label="Outperformance"
    )
    ax.fill_between(
        wealth_fund.index, wealth_fund, wealth_bm,
        where=(wealth_fund < wealth_bm),
        interpolate=True, alpha=0.25, color="blue", label="Underperformance"
    )

    ax.plot(wealth_fund, color="#FF6F3C", linewidth=1.8, label="Total Fund (TAA)")
    ax.plot(wealth_bm,   color="#0B6623", linewidth=1.4, linestyle="--", label="Composite Benchmark (SAA)")

    ax.set_title("Figure 4: Total Fund vs Composite Benchmark — Cumulative Wealth",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("Date", fontsize=11)
    ax.set_ylabel("Wealth Index (start = 1.0)", fontsize=11)
    ax.legend(loc="upper left", framealpha=0.9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(wealth_fund.index[0], wealth_fund.index[-1])
    plt.tight_layout()
    plt.show()

def plot_sharpe_bar(performance_table):
    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(performance_table.index, performance_table["Sharpe Ratio"], color="#FF69B4")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title("Figure 2: Sharpe Ratio by Asset Class")
    ax.set_ylabel("Sharpe Ratio")
    ax.set_xlabel("Asset Class")
    for bar, val in zip(bars, performance_table["Sharpe Ratio"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01, f"{val:.4f}",
                ha="center", va="bottom", fontsize=8)
    plt.tight_layout()
    plt.show()

def plot_ir_bar(performance_table):
    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(performance_table.index, performance_table["Information Ratio"], color="#FF69B4")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title("Figure 3: Information Ratio by Asset Class")
    ax.set_ylabel("Information Ratio")
    ax.set_xlabel("Asset Class")
    for bar, val in zip(bars, performance_table["Information Ratio"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01, f"{val:.4f}",
                ha="center", va="bottom", fontsize=8)
    plt.tight_layout()
    plt.show()

# SECTON 4 - APRA CHECKS AND TOTAL FUND

def plot_apra_drawdown_threshold(
    fund_returns,
    threshold: float = -0.25,
    figsize: tuple = (12, 5),
):
    wealth      = (1 + fund_returns).cumprod()
    peak        = wealth.cummax()
    drawdown    = (wealth - peak) / peak
    mdd         = drawdown.min()
    mdd_date    = drawdown.idxmin()

    fig, ax = plt.subplots(figsize=figsize)

    ax.fill_between(drawdown.index, drawdown, 0,
                    alpha=0.3, color="steelblue", label="Drawdown")
    ax.plot(drawdown.index, drawdown,
            color="steelblue", linewidth=1.2)

    ax.axhline(threshold, color="red", linewidth=1.2,
               linestyle="--", label=f"Threshold: {threshold:.0%}")

    ax.scatter(mdd_date, mdd, color="red", zorder=5, s=50)
    ax.annotate(
        f"Max: {mdd:.2%}",
        xy=(mdd_date, mdd),
        xytext=(mdd_date, mdd - 0.01),
        fontsize=9,
        color="red",
        ha="center",
    )

    ax.set_title("4.4 Maximum Drawdown Threshold", fontsize=13, fontweight="bold")
    ax.set_ylabel("Drawdown", fontsize=11)
    ax.set_xlabel("")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.1%}"))
    ax.set_xlim(drawdown.index[0], drawdown.index[-1])
    ax.set_ylim(min(mdd - 0.02, threshold - 0.02), 0.005)
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

# SECTION 5 - ATTRIBUTION

def plot_attribution(attribution_table):
    fig, ax = plt.subplots(figsize=(10, 5))
    x = range(len(attribution_table))
    width = 0.35

    ax.bar([i - width/2 for i in x], attribution_table["allocation effect"],
           width=width, label="allocation effect", color="#2196F3")
    ax.bar([i + width/2 for i in x], attribution_table["selection effect"],
           width=width, label="selection effect", color="#FF8C00")

    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(list(x))
    ax.set_xticklabels(attribution_table.index, rotation=45)
    ax.set_title("Figure 5: Attribution by Asset Class")
    ax.set_ylabel("Contribution to Active Return")
    ax.legend()
    plt.tight_layout()
    plt.show()