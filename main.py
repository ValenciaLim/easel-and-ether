import asyncio
import logging
from datetime import datetime, timedelta
from gaia_client import GaiaClient
from recall_sandbox_client import RecallSandboxClient
import yaml
import os
import json

CONFIG_PATH = 'config.yaml'
LOG_DIR = 'logs'

async def main():
    # Load config
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
    interval = config.get('loop_interval_minutes', 5)
    confidence_threshold = config.get('confidence_threshold', 0.7)
    min_trades_per_day = config.get('min_trades_per_day', 3)
    slippage_tolerance = config.get('slippage_tolerance', '0.5')
    chain = config.get('chain', 'svm')
    specific_chain = config.get('specific_chain', 'mainnet')

    os.makedirs(LOG_DIR, exist_ok=True)
    gaia = GaiaClient(config)
    recall = RecallSandboxClient(config)
    trades_today = 0
    last_trade_date = datetime.utcnow().date()

    # Example token list (should be fetched from Recall if endpoint available)
    tokens = config.get('tokens', [
        {"symbol": "SOL", "address": "So11111111111111111111111111111111111111112"},
        {"symbol": "USDC", "address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"},
        {"symbol": "BTC", "address": "9n4nbM75f5Ui33ZbPYXn59EwSgE8CGsHtAeTH5YFeJ9E"}
    ])

    while True:
        now = datetime.utcnow()
        if now.date() != last_trade_date:
            trades_today = 0
            last_trade_date = now.date()
        # Dynamic asset selection
        for token in tokens:
            # Get price and recent market data
            price_info = await recall.get_token_price(token['address'], chain, specific_chain)
            market_data = {
                'price': price_info.get('price'),
                'symbol': token['symbol'],
                'timestamp': price_info.get('timestamp'),
                'chain': chain,
                'specific_chain': specific_chain
            }
            # Narrative-driven Gaia prompt
            gaia_response = await gaia.analyze_asset(token['symbol'], market_data)
            log_entry = {
                'timestamp': now.isoformat(),
                'asset': token['symbol'],
                'gaia_decision': gaia_response,
                'market_data': market_data
            }
            log_path = os.path.join(LOG_DIR, f'{now.date()}_{token["symbol"]}.jsonl')
            with open(log_path, 'a') as logf:
                logf.write(json.dumps(log_entry) + '\n')
            # Contrarian action if confidence is high
            if (gaia_response.get('confidence', 0) >= confidence_threshold and trades_today < min_trades_per_day):
                # Determine trade direction (contrarian)
                if gaia_response.get('contrarian_action', '').upper() == 'SELL':
                    from_token = token['address']
                    to_token = tokens[1]['address'] if token['symbol'] != 'USDC' else tokens[0]['address']
                else:
                    from_token = tokens[1]['address'] if token['symbol'] != 'USDC' else tokens[0]['address']
                    to_token = token['address']
                amount = config.get('trade_amount', '1')
                reason = gaia_response.get('reason', 'Narrative turning point')
                # Execute trade via Recall
                trade_result = await recall.execute_trade(
                    from_token=from_token,
                    to_token=to_token,
                    amount=amount,
                    reason=reason,
                    slippage_tolerance=slippage_tolerance,
                    from_chain=chain,
                    from_specific_chain=specific_chain,
                    to_chain=chain,
                    to_specific_chain=specific_chain
                )
                log_entry['trade'] = trade_result
                trades_today += 1
                with open(log_path, 'a') as logf:
                    logf.write(json.dumps({'trade': trade_result, 'timestamp': now.isoformat()}) + '\n')
        await asyncio.sleep(interval * 60)

if __name__ == '__main__':
    asyncio.run(main()) 