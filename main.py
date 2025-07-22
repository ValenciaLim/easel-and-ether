import asyncio
import yaml
import os
import json
from datetime import datetime, timedelta
from trade_counter import get_trade_counts, increment_trade, reset_trade_counts
from trade_executor import execute_trade
from charting import generate_chart_snapshot
from gaia_client import gaia_client
from recall_sandbox_client import RecallSandboxClient
from coingecko_client import fetch_top_ethereum_assets, score_assets
from gaia_prompt_utils import construct_gaia_prompt
from learning_layer import record_trade, get_asset_stats

with open('config.yaml') as f:
    config = yaml.safe_load(f)

MIN_TRADES_PER_DAY = config['scheduling'].get('trades_per_day', 3)
PER_ASSET_MAX = config['trade_limits'].get('per_asset_daily', 2)
OVERALL_MAX = config['trade_limits'].get('overall_daily', 5)

recall_client = RecallSandboxClient({
    'recall_api_url': config.get('recall_api_url', 'https://api.competitions.recall.network/api'),
    'recall_api_key': config['api_keys']['recall']
})

async def trade_cycle():
    counts = get_trade_counts()
    # 1. Fetch and score top Ethereum assets
    assets = await fetch_top_ethereum_assets()
    scored = score_assets(assets)
    # 2. Build Gaia prompt
    prompt = construct_gaia_prompt(scored, n=3)
    # 3. Gaia inference
    gaia_decision = await gaia_client.gaia_infer_from_prompt(prompt)
    asset_name = gaia_decision['asset']
    action = gaia_decision['action']
    amount = gaia_decision['amount']
    reasoning = gaia_decision['reason']
    # 4. Map Gaia asset to Recall token address
    portfolio = await recall_client.get_portfolio()
    symbol_map = {t['symbol'].upper(): t['token'] for t in portfolio.get('tokens', [])}
    asset_symbol = None
    # Try to match by symbol (case-insensitive)
    for t in portfolio.get('tokens', []):
        if asset_name and (asset_name.upper() == t['symbol'].upper() or asset_name.lower() in t['name'].lower()):
            asset_symbol = t['symbol']
            break
    if not asset_symbol:
        print(f"[WARN] Gaia asset '{asset_name}' not found in Recall portfolio. Skipping trade.")
        return
    # 4.5. Check learning layer stats
    stats = get_asset_stats(asset_symbol)
    if stats['count'] >= 5 and stats['win_rate'] is not None and stats['win_rate'] < 0.3:
        print(f"[ADAPT] Skipping {asset_symbol} due to low win rate ({stats['win_rate']:.2f}) over {stats['count']} trades.")
        return
    # 5. Check trade limits
    counts = get_trade_counts()  # reload in case of concurrent updates
    asset_trades = counts['assets'].get(asset_symbol, 0)
    if action in ('Buy', 'Sell'):
        if counts['overall'] >= OVERALL_MAX:
            print(f"[WARN] Overall daily trade limit ({OVERALL_MAX}) reached. Skipping trade.")
            return
        if asset_trades >= PER_ASSET_MAX:
            print(f"[WARN] Per-asset daily trade limit ({PER_ASSET_MAX}) reached for {asset_symbol}. Skipping trade.")
            return
        # 6. Chart snapshot
        history_path = os.path.join('logs/history', f"{asset_symbol}_history.json")
        if os.path.exists(history_path):
            with open(history_path, 'r') as f:
                history = json.load(f)
        else:
            history = []
        chart_snapshot = generate_chart_snapshot(asset_symbol, history)
        # 7. Execute trade
        outcome = execute_trade(asset_symbol, action, amount=amount)
        increment_trade(asset_symbol)
        # 8. Log journal entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(timespec='minutes') + 'Z',
            "asset": asset_symbol,
            "decision": f"{action} {amount} {asset_symbol}",
            "reasoning": reasoning,
            "chart_snapshot": chart_snapshot,
            "outcome": outcome,
            "learning_stats": stats
        }
        os.makedirs('logs/journal', exist_ok=True)
        journal_path = os.path.join('logs/journal', f"journal_{datetime.utcnow().date()}.jsonl")
        with open(journal_path, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        # 9. Record trade in learning layer
        record_trade(asset_symbol, action, amount, reasoning, outcome=outcome)
    else:
        print(f"[INFO] Gaia decision: {action} for {asset_symbol}. No trade executed.")

async def daily_reset_loop():
    while True:
        now = datetime.utcnow()
        next_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        wait_seconds = (next_midnight - now).total_seconds()
        await asyncio.sleep(wait_seconds)
        counts = get_trade_counts()
        if counts['overall'] < MIN_TRADES_PER_DAY:
            print(f"[WARN] Only {counts['overall']} trades made today (minimum required: {MIN_TRADES_PER_DAY}).")
        reset_trade_counts()

async def main():
    # Start daily reset loop in background
    asyncio.create_task(daily_reset_loop())
    while True:
        await trade_cycle()
        await asyncio.sleep(config['scheduling']['trade_interval_minutes'] * 60)

if __name__ == "__main__":
    asyncio.run(main()) 