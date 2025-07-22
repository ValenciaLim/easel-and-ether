import json
from datetime import datetime

def log_journal_entry(asset, decision, reasoning, amount=None, chart_snapshot=None, extra=None):
    """
    Log a structured JSON journal entry for each trade decision.
    """
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "asset": asset,
        "decision": decision,
        "amount": amount,
        "reasoning": reasoning,
        "chart_snapshot": chart_snapshot
    }
    if extra:
        entry.update(extra)
    with open("logs/journal.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n") 