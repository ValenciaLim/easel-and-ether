# Easel-and-Ether: Adaptive Visual-Metaphor Ethereum Trading Agent

## Overview
Easel-and-Ether is a fully adaptive, cross-asset trading agent for the Ethereum network. It combines:
- **CoinGecko API**: Observes and compares top Ethereum-based assets (ERC-20 tokens) by price, volume, and volatility.
- **Heuristic Scoring**: Selects the most visually compelling assets using price change, volume, and volatility.
- **Gaia API**: Generates artistic, painterly reasoning and trade decisions using a custom prompt describing the Ethereum ecosystem.
- **Recall API**: Executes trades in the Recall trading competition using assigned token addresses.
- **Learning Layer (SQLite)**: Tracks trade outcomes and adapts strategy based on historical performance.
- **Charting**: Generates chart snapshots for journal entries.
- **Structured JSON Journal**: Logs every trade decision, reasoning, and outcome.

## High-Level Workflow
1. **Observe**: Fetch top Ethereum assets from CoinGecko.
2. **Score**: Rank assets by price change, volume, and volatility.
3. **Describe**: Build a Gaia prompt summarizing the ecosystem and top assets in artistic language.
4. **Infer**: Use Gaia to decide which asset to trade, action (buy/sell/hold), and amount.
5. **Adapt**: Check learning layer stats; skip assets with poor historical performance.
6. **Trade**: Map Gaia's asset to Recall token address and execute the trade via Recall API.
7. **Log**: Record the trade in a structured JSON journal and the learning layer.
8. **Repeat**: Loop on a schedule (asyncio-based).

## How to Run
1. Install dependencies:
   ```bash
   pip install httpx pyyaml openai jinja2 matplotlib
   ```
   (sqlite3 is included with Python stdlib)

2. Configure your `config.yaml` with Recall and Gaia API keys and scheduling/trade limits.

3. Run the agent:
   ```bash
   python main.py
   ```

## Learning Layer
- Trades are recorded in `logs/learning_layer.db` (SQLite).
- Before each trade, the agent checks win rate and average return for the asset.
- Assets with a win rate < 0.3 (if at least 5 trades) are skipped to avoid repeated losses.
- You can query stats using the `learning_layer.py` functions, e.g.:
  ```python
  from learning_layer import get_asset_stats
  print(get_asset_stats('LDO'))
  ```

## Example Journal Entry
```json
{
  "timestamp": "2025-07-22T13:05Z",
  "asset": "LDO",
  "decision": "Buy 75 LDO",
  "reasoning": "LDO's chart forms a rising spiral, like incense smoke climbing in still air. It leads the current market rhythm.",
  "chart_snapshot": "ldo_2025-07-22.png",
  "outcome": null,
  "learning_stats": {"count": 7, "win_rate": 0.43, "avg_return": 0.02}
}
```

## Dependencies
- Python 3.8+
- httpx
- pyyaml
- openai
- jinja2
- matplotlib
- sqlite3 (stdlib)

## Notes
- The agent is designed for the Recall trading competition but can be adapted for other Ethereum trading environments.
- Gaia is used strictly for inference, not chat.
- All trades use contract addresses assigned by Recall (from `/agent/portfolio`).
- The agent is fully async and can be scheduled with asyncio or APScheduler.

---

For questions or further customization, open an issue or contact the maintainer. 