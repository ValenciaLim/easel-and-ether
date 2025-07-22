import httpx

COINGECKO_MARKETS_URL = "https://api.coingecko.com/api/v3/coins/markets"

async def fetch_top_ethereum_assets(vs_currency="usd", per_page=50):
    params = {
        "vs_currency": vs_currency,
        "platform": "ethereum",
        "order": "volume_desc",
        "per_page": per_page,
        "page": 1,
        "price_change_percentage": "1h,24h,7d"
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(COINGECKO_MARKETS_URL, params=params)
        resp.raise_for_status()
        return resp.json()

def score_assets(assets, price_change_key="price_change_percentage_24h_in_currency", volume_key="total_volume", high_key="high_24h", low_key="low_24h"):
    """
    Score and rank assets by price change, volume, and volatility.
    Returns a sorted list of (asset, score) tuples, descending.
    """
    scored = []
    for asset in assets:
        # Heuristic: weighted sum of normalized metrics
        price_change = abs(asset.get(price_change_key, 0) or 0)
        volume = asset.get(volume_key, 0) or 0
        high = asset.get(high_key, 0) or 0
        low = asset.get(low_key, 0) or 0
        volatility = (high - low) / asset["current_price"] if asset["current_price"] else 0
        # Simple scoring: price change (weight 2), volume (weight 1), volatility (weight 1)
        score = 2 * price_change + 1 * (volume / 1e6) + 1 * volatility
        scored.append((asset, score))
    # Sort descending by score
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored

# Example usage:
# import asyncio
# assets = asyncio.run(fetch_top_ethereum_assets())
# print(assets[0]) 