import matplotlib.pyplot as plt

def plot_sleeve_wealth_index(manager_data, benchmark_data):
    assets = list(manager_data.keys())
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    axes = axes.flatten()
    fig_labels = ["Figure 1a", "Figure 1b", "Figure 1c", "Figure 1d", "Figure 1e"]

    for i, asset in enumerate(assets):
        mgr_wealth = (1 + manager_data[asset]).cumprod()
        bm_wealth  = (1 + benchmark_data[asset]).cumprod()

        axes[i].plot(mgr_wealth.index, mgr_wealth.values, label="Manager", color="#FF6F3C")
        axes[i].plot(bm_wealth.index, bm_wealth.values,  label="Benchmark", color="#0B6623", linestyle="--")
        axes[i].set_title(f"{fig_labels[i]}: {asset}")
        axes[i].set_xlabel("Month")
        axes[i].set_ylabel("Wealth Index")
        axes[i].tick_params(axis='x', rotation=45)
        axes[i].legend(fontsize=8)

    axes[-1].set_visible(False)
    fig.suptitle("Figure 1: Sleeve-Level Cumulative Returns — Manager vs Benchmark",
                 fontsize=13, fontweight="bold")
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
