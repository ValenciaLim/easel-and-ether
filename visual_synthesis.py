import os
import json
from statistics import mean, stdev
from datetime import datetime

HISTORY_DIR = 'logs/history'
HISTORY_LENGTH = 10  # Number of points to keep per asset
os.makedirs(HISTORY_DIR, exist_ok=True)

def _history_path(symbol):
    return os.path.join(HISTORY_DIR, f"{symbol}_history.json")

def _load_history(symbol):
    path = _history_path(symbol)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return []

def _save_history(symbol, history):
    path = _history_path(symbol)
    with open(path, 'w') as f:
        json.dump(history, f)

def describe_market_painterly(data):
    """
    Convert raw asset data into a vivid, painterly textual description of visual patterns and emotional vibes,
    using real price/volume trends from persisted history.
    """
    symbol = data.get('symbol', 'an asset')
    price = data.get('price', 0.0)
    volume = data.get('volume', 0.0)
    on_chain = data.get('on_chain', {})
    now = datetime.utcnow().isoformat() + 'Z'

    # Load and update history
    history = _load_history(symbol)
    history.append({'timestamp': now, 'price': price, 'volume': volume})
    if len(history) > HISTORY_LENGTH:
        history = history[-HISTORY_LENGTH:]
    _save_history(symbol, history)

    # Compute trends
    prices = [h['price'] for h in history if h['price'] is not None]
    volumes = [h['volume'] for h in history if h['volume'] is not None]
    price_trend = 'unknown'
    volume_trend = 'unknown'
    volatility = 0.0

    if len(prices) >= 2:
        delta = prices[-1] - prices[0]
        pct = (delta / prices[0]) if prices[0] else 0
        if abs(pct) < 0.01:
            price_trend = 'flat'
        elif pct > 0.01:
            price_trend = 'rising'
        elif pct < -0.01:
            price_trend = 'falling'
        if len(prices) > 2:
            volatility = stdev(prices)
            if volatility > 0.03 * mean(prices):
                price_trend = 'volatile'
    if len(volumes) >= 2:
        delta_v = volumes[-1] - volumes[0]
        pct_v = (delta_v / volumes[0]) if volumes[0] else 0
        if abs(pct_v) < 0.05:
            volume_trend = 'steady'
        elif pct_v > 0.05:
            volume_trend = 'surging'
        elif pct_v < -0.05:
            volume_trend = 'dropping'

    # Metaphor templates
    metaphors = {
        'rising': f"The chart for {symbol} forms a rising spiral, like smoke from a bonfire; momentum building steadily.",
        'falling': f"The chart for {symbol} drips downward, like paint running from a canvas; energy dissipating.",
        'volatile': f"{symbol} whirls in a storm of brushstrokes, price and volume clashing in vivid bursts.",
        'flat': f"{symbol} rests in muted tones, the market calm and still as a pond at dawn.",
        'unknown': f"The market for {symbol} is a blank canvas, awaiting the first stroke."
    }
    volume_flavors = {
        'surging': "Volume surges in bold strokes, amplifying the movement.",
        'dropping': "Volume fades, colors thinning as the energy wanes.",
        'steady': "Volume remains steady, a gentle rhythm beneath the surface.",
        'unknown': "Volume is an underpainting, subtle and subdued."
    }
    on_chain_flavors = [
        "On-chain activity flickers at the edges, hinting at hidden currents.",
        "Blockchain flows ripple beneath the surface, subtle but persistent.",
        "Smart contract calls add texture, like impasto on a painted surface.",
        "NFT transfers sparkle like flecks of gold in the paint."
    ]
    import random
    on_chain_phrase = random.choice(on_chain_flavors) if on_chain else ""

    # Compose description
    desc = metaphors.get(price_trend, metaphors['unknown'])
    desc += " " + volume_flavors.get(volume_trend, volume_flavors['unknown'])
    if on_chain_phrase:
        desc += " " + on_chain_phrase
    return desc 