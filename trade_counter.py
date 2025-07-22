import os
import json
from datetime import datetime

TRADE_COUNT_DIR = 'logs'

def _trade_count_path():
    date_str = datetime.utcnow().strftime('%Y%m%d')
    return os.path.join(TRADE_COUNT_DIR, f'trade_counts_{date_str}.json')

def _load_counts():
    path = _trade_count_path()
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {"overall": 0, "assets": {}}

def _save_counts(counts):
    path = _trade_count_path()
    with open(path, 'w') as f:
        json.dump(counts, f)

def increment_trade(asset):
    counts = _load_counts()
    counts["overall"] += 1
    counts["assets"][asset] = counts["assets"].get(asset, 0) + 1
    _save_counts(counts)

def get_trade_counts():
    return _load_counts()

def reset_trade_counts():
    _save_counts({"overall": 0, "assets": {}}) 