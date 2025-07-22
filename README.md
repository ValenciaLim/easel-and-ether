# Autonomous Apes: Narrative-Driven Crypto Trading Agent (Recall + Gaia)

## Overview
This agent is designed for the Autonomous Apes trading competition on the Recall platform, and is built to qualify for the "Live Trading Agents built on Gaia" bounty.

**Key innovation:** Gaia is used as a creative, narrative-driven inference engine. The agent treats the market as a psychological story, and makes real trading decisions based on Gaia's structured, explainable output—not just as a chat interface.

---

## How It Works

1. **Every 5 minutes:**
    - Pulls live market data (price, volume, etc.) for multiple assets from Recall's sandbox API.
    - Sends a narrative-driven prompt (using a Jinja2 template) to Gaia, describing recent market behavior for each asset.
    - Gaia responds with structured JSON, e.g.:
      ```json
      {
        "asset": "ETH",
        "narrative_stage": "bull trap",
        "emotion": "euphoria",
        "expected_crowd_behavior": "buy breakout",
        "contrarian_action": "SELL",
        "confidence": 0.84,
        "reason": "Excessive optimism and price acceleration — likely reversal"
      }
      ```
    - If Gaia's confidence is above a configurable threshold, the agent places a real trade using Recall's API.
    - Every Gaia "thought" and trade is logged in structured JSON for transparency and explainability.
    - The agent ensures at least 3 trades per day.

2. **Creative Features:**
    - Uses Gaia to detect market psychology and narrative tension.
    - Dynamic asset selection: trades any asset Recall exposes (BTC, ETH, SOL, etc.).
    - Contrarian bias: acts against the crowd at emotional turning points.
    - Volatility + confidence filtering to reduce noise.
    - All reasoning and actions are logged for auditability and bounty requirements.

---

## Why This Qualifies for the Gaia Bounty

- **Gaia is the core inference engine:**
  - Gaia is not just a chat interface. Its structured, creative output directly determines the agent's trading actions.
  - The agent is autonomous: it uses Gaia's reasoning to make real, live trading decisions.
  - All trades are explainable and justified by Gaia's narrative/psychological analysis.

- **Not just chat:**
  - There is no user-facing chat loop. Gaia is used for inference, not conversation.
  - The agent's loop is:
    1. Pull market data
    2. Send to Gaia for narrative inference
    3. Parse Gaia's structured output
    4. If confidence is high, execute a trade
    5. Log all reasoning and actions

---

## Example Agent Loop (Pseudocode)

```python
for each asset:
    market_data = get_market_data()
    gaia_decision = gaia.analyze_asset(asset, market_data)
    if gaia_decision['confidence'] > threshold:
        place_trade(gaia_decision['contrarian_action'])
    log(gaia_decision, trade)
```

---

## How to Run
1. Install requirements: `pip install -r requirements.txt`
2. Set up your `config.yaml` with Recall and Gaia API keys, tokens, and parameters.
3. Run the agent: `python main.py`

---

## Customization
- Edit `prompt_template.j2` to enhance the narrative/psychological flavor.
- Adjust config parameters for trading frequency, thresholds, and asset selection.

---

## Contact
For questions or to discuss creative extensions, open an issue or contact the author. 