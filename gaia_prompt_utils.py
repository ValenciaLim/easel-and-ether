import datetime

def construct_gaia_prompt(scored_assets, n=3, ecosystem_summary=None):
    """
    Build a Gaia prompt summarizing the Ethereum ecosystem and artistically describing the top n assets.
    scored_assets: list of (asset, score) tuples, sorted descending.
    Returns: prompt string
    """
    now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
    top_assets = [a for a, _ in scored_assets[:n]]
    # Ecosystem summary
    if not ecosystem_summary:
        ecosystem_summary = f"As of {now}, Ethereum's DeFi and token landscape is vibrant and ever-shifting."
    # Artistic descriptions
    descs = []
    for asset in top_assets:
        name = asset.get('name', 'Unknown')
        symbol = asset.get('symbol', '').upper()
        price = asset.get('current_price', '?')
        change = asset.get('price_change_percentage_24h_in_currency', 0)
        vol = asset.get('total_volume', 0)
        high = asset.get('high_24h', 0)
        low = asset.get('low_24h', 0)
        metaphor = (
            f"{name} ({symbol}) trades at ${price:.2f}, its chart forms "
            f"{'a rising spiral' if change > 0 else 'a falling ribbon'}, "
            f"with a 24h change of {change:+.2f}%. "
            f"Volume swells to {vol:,.0f}, volatility dances between {low:.2f} and {high:.2f}."
        )
        descs.append(metaphor)
    desc_block = '\n'.join(descs)
    # Compose prompt
    prompt = (
        f"{ecosystem_summary}\n"
        f"Here are the most visually interesting assets today:\n"
        f"{desc_block}\n"
        "Which asset should I trade next? Should I buy, sell, or hold, and how much? "
        "Respond in JSON with asset, action, amount, and a painterly reason."
    )
    return prompt 