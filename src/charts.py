import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


def plot_fund_vs_benchmark(
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