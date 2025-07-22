import sqlite3
from datetime import datetime

DB_PATH = 'logs/learning_layer.db'

# Initialize DB and table if not exists
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            asset TEXT,
            action TEXT,
            amount REAL,
            outcome REAL,
            reasoning TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Record a trade
def record_trade(asset, action, amount, reasoning, outcome=None, timestamp=None):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    ts = timestamp or datetime.utcnow().isoformat(timespec='minutes') + 'Z'
    c.execute('''
        INSERT INTO trades (timestamp, asset, action, amount, outcome, reasoning)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (ts, asset, action, amount, outcome, reasoning))
    conn.commit()
    conn.close()

# Update outcome for a trade (by id)
def update_outcome(trade_id, outcome):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE trades SET outcome = ? WHERE id = ?', (outcome, trade_id))
    conn.commit()
    conn.close()

# Query past trades for an asset
def get_trades_for_asset(asset):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM trades WHERE asset = ? ORDER BY timestamp DESC', (asset,))
    rows = c.fetchall()
    conn.close()
    return rows

# Compute basic stats (win rate, avg return) for an asset
def get_asset_stats(asset):
    trades = get_trades_for_asset(asset)
    n = len(trades)
    if n == 0:
        return {'count': 0, 'win_rate': None, 'avg_return': None}
    wins = [t for t in trades if t[5] is not None and t[5] > 0]
    avg_return = sum([t[5] for t in trades if t[5] is not None]) / len([t for t in trades if t[5] is not None])
    win_rate = len(wins) / n
    return {'count': n, 'win_rate': win_rate, 'avg_return': avg_return} 