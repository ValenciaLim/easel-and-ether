import yaml
import asyncio
from recall_sandbox_client import RecallSandboxClient

with open('config.yaml') as f:
    config = yaml.safe_load(f)

recall_client = RecallSandboxClient({
    'recall_api_url': config.get('recall_api_url', 'https://api.sandbox.competitions.recall.network/api'),
    'recall_api_key': config['api_keys']['recall']
})

# Global cache for symbol-to-address mapping
_symbol_to_address = None

async def _get_symbol_to_address():
    global _symbol_to_address
    if _symbol_to_address is None:
        portfolio = await recall_client.get_portfolio()
        # Build mapping: symbol (upper) -> address
        _symbol_to_address = {t['symbol'].upper(): t['token'] for t in portfolio.get('tokens', [])}
    return _symbol_to_address

def execute_trade(symbol, decision, amount=1, slippage_tolerance=0.5, counter_asset='ETH'):
    """
    Execute a trade (buy/sell) for the given asset using Recall's trade execution API.
    """
    async def _do_trade():
        symbol_map = await _get_symbol_to_address()
        symbol_u = symbol.upper()
        counter_u = counter_asset.upper()
        if symbol_u not in symbol_map or counter_u not in symbol_map:
            print(f"[WARN] Symbol {symbol} or counter asset {counter_asset} not found in Recall portfolio. Skipping trade.")
            return None
        from_token, to_token = (symbol_map[counter_u], symbol_map[symbol_u]) if decision == 'Buy' else (symbol_map[symbol_u], symbol_map[counter_u])
        reason = f"Automated {decision.lower()} by Easel-and-Ether agent."
        # Use default chain params (can be extended)
        from_chain = to_chain = 'ethereum'
        from_specific_chain = to_specific_chain = 'mainnet'
        result = await recall_client.execute_trade(
            from_token=from_token,
            to_token=to_token,
            amount=amount,
            reason=reason,
            slippage_tolerance=slippage_tolerance,
            from_chain=from_chain,
            from_specific_chain=from_specific_chain,
            to_chain=to_chain,
            to_specific_chain=to_specific_chain
        )
        print(f"Trade executed: {result}")
        return result
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_do_trade()) 