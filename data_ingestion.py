from recall_sandbox_client import RecallSandboxClient
import yaml

with open('config.yaml') as f:
    config = yaml.safe_load(f)

recall_client = RecallSandboxClient({
    'recall_api_url': config.get('recall_api_url', 'https://api.sandbox.competitions.recall.network/api'),
    'recall_api_key': config['api_keys']['recall']
})

async def fetch_multi_asset_data(asset):
    # asset is a dict with 'symbol' and 'address'
    address = asset['address']
    symbol = asset['symbol']
    price_data = await recall_client.get_token_price(address)
    token_info = await recall_client.get_token_info(address)
    return {
        'symbol': symbol,
        'address': address,
        'price': price_data.get('price'),
        'volume': token_info.get('volume', 0.0),
        'on_chain': token_info.get('on_chain', {})
    } 