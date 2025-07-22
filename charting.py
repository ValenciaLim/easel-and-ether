import os
import matplotlib.pyplot as plt
from datetime import datetime

def generate_chart_snapshot(symbol, history):
    """
    Generate a price/volume chart for the asset using its history and save as PNG.
    Returns the file path to the saved chart, or None if not enough data.
    """
    if not history or len(history) < 2:
        return None
    timestamps = [h['timestamp'] for h in history]
    prices = [h['price'] for h in history]
    volumes = [h['volume'] for h in history]
    # Prepare output directory
    chart_dir = os.path.join('logs', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    # File name with timestamp
    fname = f"{symbol}_{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}.png"
    fpath = os.path.join(chart_dir, fname)
    # Plot
    fig, ax1 = plt.subplots(figsize=(8, 4))
    color = 'tab:blue'
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Price', color=color)
    ax1.plot(timestamps, prices, color=color, marker='o', label='Price')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.legend(loc='upper left')
    ax2 = ax1.twinx()
    color = 'tab:orange'
    ax2.set_ylabel('Volume', color=color)
    ax2.bar(timestamps, volumes, color=color, alpha=0.3, label='Volume')
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.legend(loc='upper right')
    plt.title(f"{symbol} Price & Volume History")
    plt.xticks(rotation=45, ha='right', fontsize=8)
    plt.tight_layout()
    plt.savefig(fpath)
    plt.close(fig)
    return fpath 